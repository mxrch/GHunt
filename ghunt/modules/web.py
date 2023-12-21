from ghunt.helpers.utils import get_httpx_client
from ghunt.objects.base import GHuntCreds
from ghunt.objects.encoders import GHuntEncoder
from ghunt.apis.peoplepa import PeoplePaHttp
from ghunt.apis.drive import DriveHttp
from ghunt.helpers import gmaps, playgames, auth, calendar
from ghunt.helpers.drive import get_users_from_file

import json
import httpx
import humanize
import uvicorn
from uhttp import App, Request, Response


app = App()


def _jsonify(obj):
    return Response(
        status=200,
        headers={'content-type': 'application/json'},
        body=json.dumps(obj, cls=GHuntEncoder, indent=4).encode()
    )


@app.get(r'/email/(?P<email>[\w@.-]+)')
async def _email(request: Request):
    body = {
        'account': {
            'id': '',
            'name': '',
            'email': '',
            'picture': '',
            'cover': '',
            'last_updated': ''
        },
        'maps': {
            'stats': {},
            'reviews': [],
            'photos': [],
        },
        'calendar': {
            'details': {},
            'events': []
        },
        'player': {
            'id': '',
            'name': '',
            'gamertag': '',
            'title': '',
            'avatar': '',
            'banner': '',
            'experience': '',
        }
    }

    people_pa = PeoplePaHttp(request.state['creds'])
    found, person = await people_pa.people_lookup(
        request.state['client'],
        request.params['email'],
        params_template='max_details'
    )
    if not found:
        return _jsonify(body)
    body['account'].update(
        id=person.personId,
        name=person.names['PROFILE'].fullname,
        email=person.emails['PROFILE'].value,
        picture=person.profilePhotos['PROFILE'].url,
        cover=person.coverPhotos['PROFILE'].url,
        last_updated=person.sourceIds['PROFILE'].lastUpdated.strftime(
            '%Y/%m/%d %H:%M:%S (UTC)'
        )
    )

    err, stats, reviews, photos = await gmaps.get_reviews(
        request.state['client'],
        person.personId
    )
    if not err:
        body['maps'].update(stats=stats, reviews=reviews, photos=photos)

    found, details, events = await calendar.fetch_all(
        request.state['creds'],
        request.state['client'],
        request.params['email']
    )
    if found:
        body['calendar'].update(details=details, events=events)

    player_results = await playgames.search_player(
        request.state['creds'],
        request.state['client'],
        request.params['email']
    )
    if player_results:
        _, player = await playgames.player(
            request.state['creds'],
            request.state['client'],
            player_results[0].id
        )
        body['games'].update(
            id=player.profile.id,
            name=player.profile.display_name,
            gamertag=player.profile.gamertag,
            title=player.profile.title,
            avatar=player.profile.avatar_url,
            banner=player.profile.banner_url_landscape,
            experience=player.profile.experience_info.current_xp,
        )

    return _jsonify(body)


@app.get(r'/gaia/(?P<gaia>\d+)')
async def _gaia(request: Request):
    body = {
        'id': '',
        'name': '',
        'email': '',
        'picture': '',
        'cover': '',
        'last_updated': ''
    }

    people_pa = PeoplePaHttp(request.state['creds'])
    found, person = await people_pa.people(
        request.state['client'],
        request.params['gaia'],
        params_template='max_details'
    )
    if found:
        body.update(
            id=person.personId,
            name=person.names['PROFILE'].fullname,
            email=person.emails['PROFILE'].value,
            picture=person.profilePhotos['PROFILE'].url,
            cover=person.coverPhotos['PROFILE'].url,
            lastUpdated=person.sourceIds['PROFILE'].lastUpdated.strftime(
                '%Y/%m/%d %H:%M:%S (UTC)'
            )
        )

    return _jsonify(body)


@app.get(r'/drive/(?P<drive>\w+)')
async def _drive(request: Request):
    body = {
        'id': '',
        'title': '',
        'size': '',
        'icon': '',
        'thumbnail': '',
        'description': '',
        'created': '',
        'modified': '',
        'users': [],
    }

    drive = DriveHttp(request.state['creds'])
    found, file = await drive.get_file(
        request.state['client'], request.params['drive']
    )
    if found:
        body.update(
            id=file.id,
            title=file.title,
            size=humanize.naturalsize(file.file_size),
            icon=file.icon_link,
            thumbnail=file.thumbnail_link,
            description=file.description,
            created=file.created_date.strftime('%Y/%m/%d %H:%M:%S (UTC)'),
            modified=file.modified_date.strftime('%Y/%m/%d %H:%M:%S (UTC)'),
            users=get_users_from_file(file)
        )

    return _jsonify(body)


@app.after
def _cors(request: Request, response: Response):
    if request.headers.get('origin'):
        response.headers['access-control-allow-origin'] = '*'


async def hunt(as_client: httpx.AsyncClient, host: str, port: int, api: bool):
    @app.startup
    def setup_ghunt(state):
        state['client'] = as_client or get_httpx_client()
        state['creds'] = GHuntCreds()
        state['creds'].load_creds()
        if not state['creds'].are_creds_loaded():
            raise RuntimeError('Missing credentials')
        if not auth.check_cookies(state['creds'].cookies):
            raise RuntimeError('Invalid cookies')

    if not api:
        from ghunt import static
        app.mount(static.app)

    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

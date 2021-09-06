import os
from py4web import action, request, DAL, Field, Session, Cache, HTTP
from py4web.core import Fixture, Template
from py4web.utils.xapi import SafeFixtures
from types import SimpleNamespace



cache = Cache(size=1000)

# define database and tables
db = DAL(
    "sqlite://storage.db", folder=os.path.join(os.path.dirname(__file__), "databases")
)
db.define_table("todo", Field("info"))
db.commit()


# some init
SafeFixtures.Fixture = Fixture
SafeFixtures.HTTP = HTTP


class RequiresUser(Fixture):

    def __init__(self, session):
        self.__prerequisites__ = [session]
        self.session = session

    def on_request(self):
        user = self.session.get('user')
        if not user or not user.get('id'):
            raise HTTP(401)


class SF(SafeFixtures):
    session = Session(secret="some secret")
    index_html = Template('index.html')
    db = db
    user_in = RequiresUser(session)


sf = SF()

# example index page using session, template and vue.js
@action("index")  # the function below is exposed as a GET action
@sf
def index():
    sf.session["counter"] = sf.session.get("counter", 0) + 1
    sf.session["user"] = {"id": 1}  # store a user in session
    sf.index_html
    return dict(session=sf.session)


@action("api")  # a GET API function
@sf.use(sf.user_in)
def todo():
    db = sf.db
    return dict(items=db(db.todo).select(orderby=~db.todo.id).as_list())


@action("api", method="POST")
@sf.use(sf.user_in)
def todo():
    db = sf.db
    return dict(id=db.todo.insert(info=request.json.get("info")))


@action("api/<id:int>", method="DELETE")
@sf.use(sf.user_in)
def todo(id):
    db = sf.db
    db(db.todo.id == id).delete()
    return dict()


# example of caching
@action("uuid")
@cache.memoize(expiration=5)  # here we cache the result for 5 seconds
def uuid():
    import uuid

    return str(uuid.uuid4())

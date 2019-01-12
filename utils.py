from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound


def get_or_create(session, model, **kwargs):
    """
    Get or create a model instance while preserving integrity.
    """
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        try:
            with session.begin_nested():
                instance = model(**kwargs)
                session.add(instance)
                return instance, True
        except IntegrityError:
            return session.query(model).filter_by(**kwargs).one(), False


def get_or_create_multiple(session, model, data):
    """
    Get or create multiple instances of model. For simplest objects which only have the name field we can pass
    a list of names only instead of a list of dictionaries as kwargs for each object.
    :param session: db_session, Database session object.
    :param model: model to get or create.
    :param data: Union[list, dict], data to process
    :return: objs: list, list of objects
    """
    objs = []
    for item in data:
        obj = None
        if isinstance(data, str):
            obj, _ = get_or_create(session, model, name=item)
        elif isinstance(data, dict):
            obj, _ = get_or_create(session, model, **item)
        objs.append(obj)

    return objs

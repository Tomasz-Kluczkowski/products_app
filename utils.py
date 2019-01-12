from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from database.database import Base, db_session


def get_or_create(model, **kwargs):
    """
    Get or create a model instance while preserving integrity.
    :param model: model to get or create.
    :return: tuple, Tuple of instance of the model and boolean reflecting if object was or was not created.
    """
    try:
        return db_session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        try:
            with db_session.begin_nested():
                instance = model(**kwargs)
                db_session.add(instance)
                return instance, True
        except IntegrityError:
            return db_session.query(model).filter_by(**kwargs).one(), False


def get_or_create_multiple(model, data):
    """
    Get or create multiple instances of model. For simplest objects which only have the name field we can pass
    a list of names only instead of a list of dictionaries as kwargs for each object.
    :param model: model to get or create.
    :param data: Union[list, dict], data to process
    :return: objs: list, list of objects
    """
    objs = []
    for item in data:
        obj = None
        if isinstance(data, str):
            obj, _ = get_or_create(model, name=item)
        elif isinstance(data, dict):
            obj, _ = get_or_create(model, **item)
        objs.append(obj)

    return objs


def get_class_by_table_name(tablename):
    """Return class reference mapped to table.
    :param tablename: str, String with name of table.
    :return: Class reference or None.
    """
    for c in Base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c

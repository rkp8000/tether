__all__ = ['connect', 'models']


def get_or_create(session, model, id, **kwargs):
    """Return or create new row using database session."""

    potential_instance = session.query(model).get(id)

    if potential_instance:
        instance = potential_instance
    else:
        instance = model(id=id, **kwargs)
        session.add(instance)

    return instance
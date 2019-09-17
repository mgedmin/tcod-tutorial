def component(name):
    """Decorator for defining Entity component slots.

    All it does is update the component's owner when you assign a new component
    to an entity.
    """

    def getter(self):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name)

    def setter(self, value):
        # it might be nice to set the owner of the old value to None, if there
        # was an old value
        # it might be nice to make sure the component doesn't already have an
        # owner
        # neither of the two cases above ever happens in the game so we can
        # ignore them for now
        self.__dict__[name] = value
        if value is not None:
            value.owner = self  # <-- this is why @component exists

    getter.__name__ = setter.__name__ = name
    return property(getter, setter)

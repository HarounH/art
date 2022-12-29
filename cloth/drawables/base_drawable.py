# TODO: Extend to non-OpenGL backends?
class BaseDrawable:

    def update(self, *args, **kwargs) -> None:
        ...

    def create_buffers(self) -> None:
        pass

    def draw(self) -> None:
        pass

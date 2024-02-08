import pathlib
import os
import tempfile


class Environment(object):
    """
    Environment is an internal class that manages the environment for a Simulation, mainly files.  A new environment is
    created before each :class:`simulation.Simulation` is called.  The environment can be customized using the
    :function:`simulation.Simulator.setup()` function.  The environment won't be cleaned up until after the
    :class:`loss.Loss` function is calculated and can be customized using the
    :function:`simulation.Simulator.cleanup()` function.  Also handle any remote execution stuff here.

    :ivar output: an unused variable left to the user to populate.  Provides a convenient way to move simulator output
    between :function:`simulation.Simulator.run() and :function:`simulation.Simulator.extract()`
    :type output: Any

    """

    def __init__(self, cwd: str | os.PathLike | None = None) -> None:
        """Constructor"""
        super().__init__()
        # the Original Working Directory that will be returned to during cleanup
        if cwd is None:
            self._owd: pathlib.Path = pathlib.Path(os.getcwd())
        else:
            self._owd: pathlib.Path = pathlib.Path(os.fspath(cwd))
        self.output = None
        # the Current Working Directory of this environment
        self._cwd = self._owd
        # the "stack" of temporary objects that need to be cleaned up at cleanup time
        self._stack: list[tempfile.TemporaryDirectory | tempfile.TemporaryFile] = list()

    def get_owd(self) -> pathlib.Path:
        """Get the Original Working Directory for this Environment
        rtype: pathlib.Path"""
        return self._owd

    def get_cwd(self) -> pathlib.Path:
        """Get the Current Working Directory for this Environment
        rtype: pathlib.Path"""
        return self._cwd

    def cd(self, path: str | os.PathLike | None = None) -> pathlib.Path:
        """Changes the current Directory for this Environment.  If no path given, resets it to cwd.

        :param path: the path to change to.  If None, cwd is used
        :type path: class:`os.PathLike`

        :return: The current directory after the CD
        :rtype: pathlib.Path
        """
        if path is None:
            os.chdir(self._cwd)
        else:
            path = pathlib.Path(path).absolute()
            self._cwd = path
            os.chdir(path)
        return self._cwd

    def tmp_dir(self, dir: str | os.PathLike | None = None, keep: bool = False) -> pathlib.Path:
        """Creates a unique temporary directory for the simulator to work in.

        :param dir: directory to use as parent.  If `None`, the system temp directory is used
        :type dir: str | os.PathLike | None

        :param keep: Optional parameter to keep the unique directory instead of deleting it.  Defaults to false.
        :type keep: bool

        :return: The path of the new directory
        :rtype: pathlib.Path"""
        path = tempfile.TemporaryDirectory(ignore_cleanup_errors=True, dir=dir, delete=keep)
        if keep:
            self._stack.append(path)
        return self.cd(path.name)

    def tmp_file(self, dir: str | os.PathLike | None = None, keep: bool = False) -> tempfile.NamedTemporaryFile:
        """Creates a unique temporary file for the simulator to use.

        :param dir: directory to use as parent.  If `None`, the system temp directory is used
        :type dir: str | os.PathLike | None

        :param keep: Optional parameter to keep the unique directory instead of deleting it.  Defaults to false.
        :type keep: bool

        :return: The Filelike object that points to the new file
        :rtype: tempfile.NamedTemporaryFile"""
        path = tempfile.NamedTemporaryFile(delete_on_close=False, dir=dir, delete=keep)
        if keep:
            self._stack.append(path)
        return path

    def cleanup(self) -> None:
        """Cleanup the environment by deleting any temporary files or folders that need to and returning to the
        Original Working Directory"""
        os.chdir(self._owd)
        for tmp in self._stack:
            tmp.cleanup()
        self._stack = list()

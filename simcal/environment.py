from __future__ import annotations

import os
import pathlib
import tempfile
from typing import Self

from simcal.utility_functions import bash


class Environment(object):
    """
    Environment is an internal class that manages the environment for a Simulation, mainly files.  A new environment is
    created before each :class:`simulation.Simulation` is called.  The environment can be customized using the
    :function:`simulation.Simulator.setup()` function.  The environment won't be cleaned up until after the
    :class:`loss.Loss` function is calculated and can be customized using the
    :function:`simulation.Simulator.cleanup()` function.  Also handle any remote execution stuff here.

#    :ivar output: an unused variable left to the user to populate.  Provides a convenient way to move simulator output
#    between :function:`simulation.Simulator.run() and :function:`simulation.Simulator.extract()`
#    :type output: Any

    """

    def __init__(self, cwd: str | os.PathLike | None = None) -> None:
        """Constructor"""
        super().__init__()
        # the Original Working Directory that will be returned to during cleanup
        if cwd is None:
            self._owd: pathlib.Path = pathlib.Path(os.getcwd())
        else:
            self._owd: pathlib.Path = pathlib.Path(os.fspath(cwd))
        #        self.output = None
        # the Current Working Directory of this environment
        self._cwd = self._owd
        # the "stack" of temporary objects that need to be cleaned up at cleanup time
        self._dir_stack: list[tempfile.TemporaryDirectory] = list()
        self._file_stack: list[tempfile.TemporaryFile] = list()

        self._use_cwd = os.PathLike is not None

    def use_cwd(self) -> Self:
        """
        Change the default behavior to use the internal CWD as the root folder for future temporary objects
        """
        self._use_cwd = True
        return Self

    def use_sys_tmp(self) -> Self:
        """
        Change the default behavior to use the system temp folder as the root folder for future temporary objects
        """
        self._use_cwd = False
        return Self

    def get_owd(self) -> pathlib.Path:
        """Get the Original Working Directory for this Environment
        :return: Original Working Directory
        :rtype: pathlib.Path"""
        return self._owd

    def get_cwd(self) -> pathlib.Path:
        """Get the Current Working Directory for this Environment
        :return: Current Working Directory
        :rtype: pathlib.Path"""
        return self._cwd

    def cd(self, path: str | os.PathLike) -> Self:
        """Changes the current Directory for this Environment.

        :param path: the path to change to.
        :type path: class:`os.PathLike`

        :return: Self
        :rtype: Self
        """
        self._cwd = self.path(path)
        return self

    def tmp_dir(self, directory: str | os.PathLike | None = None, keep: bool = False) -> pathlib.Path:
        """Creates a unique temporary directory for the simulator to work in.

        :param directory: directory to use as parent.  If `None`, the default temp directory (see use_cwd and use_sys_tmp) is used
        :type directory: str | os.PathLike | None

        :param keep: Optional parameter to keep the unique directory instead of deleting it.  Defaults to false.
        :type keep: bool

        :return: The path of the new directory
        :rtype: pathlib.Path"""
        if self._use_cwd and directory is None:
            directory = self._cwd
        path = tempfile.TemporaryDirectory(ignore_cleanup_errors=True, dir=directory, delete=False)
        if not keep:
            self._dir_stack.append(path)
        self.cd(path.name)
        return self._cwd

    def tmp_file(self, directory: str | os.PathLike | None = None, keep: bool = False, encoding: str | None = None,
                 mode: str = 'w') -> tempfile.NamedTemporaryFile:
        """Creates a unique temporary file for the simulator to use.

        :param directory: directory to use as parent.  If `None`, the system temp directory or cwd is used depending on use_cwd
        :type directory: str | os.PathLike | None

        :param keep: Optional parameter to keep the temporary file instead of deleting it.  Defaults to false.
        :type keep: bool

        :param encoding: Optional parameter to specify the file encoding.
        :type encoding: str | None

        :param mode: Optional parameter to specify the mode to open, defaults to 'w'
        :type mode: str

        :return: The Filelike object that points to the new file
        :rtype: tempfile.NamedTemporaryFile"""
        if self._use_cwd and directory is None:
            directory = self._cwd
        path = tempfile.NamedTemporaryFile(delete_on_close=False, dir=directory, delete=False, encoding=encoding,
                                           mode=mode)
        if not keep:
            self._file_stack.append(path)
        return path

    def cleanup(self) -> None:
        """Cleanup the environment by deleting any temporary files or folders that need to and returning to the
        Original Working Directory"""
        # os.chdir(self._owd)
        for tmp in self._file_stack:
            tmp.close()
        self._file_stack = list()

        for tmp in self._dir_stack:
            tmp.cleanup()
        self._dir_stack = list()

    # TODO document things under here
    def bash(self, command, args=None, std_in=None):  # TODO account for remote ex
        # os.chdir(self._cwd)
        return bash(command, args, std_in, cwd=self._cwd)

    def open(self, file, *args, **kwargs):
        return open(self.path(file), *args, **kwargs)

    def path(self, path: str | os.PathLike) -> pathlib.Path:
        if os.path.isabs(path):
            path = pathlib.Path(path)
        else:
            path = pathlib.Path(self._cwd / path).resolve()
        return path

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.cleanup()

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
from setuptools.command.test import test as TestCommand

from exlobe.version import VERSION


class test(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        from pytest import main
        main(self.test_args)


setup(
    name='exlobe',
    version=VERSION,
    packages=['exlobe'],
    description='An web-based essay outlining tool',
    author='Jae-Myoung Yu',
    author_email='euphoris' '@' 'gmail.com',
    url='https://bitbucket.org/euphoris/lifemetr',
    install_requires=['flask', 'sqlalchemy'],
    tests_require=['pytest'],
    cmdclass={'test': test}
)

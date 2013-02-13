import os
import sys
from setuptools import setup
from setuptools import find_packages


setup(name='audit',
      version='0.0.0',
      url='',
      author="Kura",
      author_email="kura@kura.io",
      description="",
      long_description=file(
          os.path.join(
              os.path.dirname(__file__),
              'README.rst'
          )
      ).read(),
      license='BSD',
      platforms=['linux'],
      packages=['audit'],
      install_requires=[
          'EVELink==0.2.0',
          'Flask==0.9',
          'Jinja2==2.6',
          'Flask_WTF==0.8',
          'WTForms==1.0.2',
          'requests==0.14.2',
      ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
      ],
      )

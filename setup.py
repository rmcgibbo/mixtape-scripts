from setuptools import setup

setup(name='mixtape-scripts',
      packages=['mixtape_scripts'],
      author='Robert T. McGibbon',
      entry_points = {'console_scripts': [
            'mixtape-convert-chunked-project = mixtape_scripts.convert_chunked_project:main',
            'mixtape-featurize-trajset = mixtape_scripts.featurize_trajset:main'
            ]}
      )

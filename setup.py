from setuptools import setup
setup(
  name = 'nornir_csv',
  packages = ['nornir_csv'],
  version = '0.1.2',
  license='apache-2.0',
  description = 'CSV Inventory for nornir with hosts, groups and defaults.',
  long_description = open('README','r',encoding='utf-8').read(),
  long_description_content_type="text/markdown",
  author = 'Matheus Augusto da Silva',
  author_email = 'a.matheus26@hotmail.com',
  url = 'https://github.com/matman26/nornir_csv',
  download_url = 'https://github.com/matman26/nornir_csv/archive/refs/tags/v0.1.tar.gz',
  keywords = ['nornir', 'csv', 'inventory', 'plugin'],
  install_requires=[
          'nornir',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
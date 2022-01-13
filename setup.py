import os
from setuptools import setup, find_packages

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open('ctu/_version.py') as f:
    exec(f.read())

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'opencv-python-headless==4.5.2.54',
    'numpy==1.19.5',
    'matplotlib==3.2.0'
]

setup(
    # This is the name of your PyPI-package.
    name='ctu',

    # Update the version number for new releases
    version=__version__,

    # description='Testing installation of Package',
    description='A python package to perform same transformation to coco-annotation as performed on the image.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Mohit Rajput',
    author_email='mohitrajput901@gmail.com',
    maintainer='Mohit Rajput',
    maintainer_email='mohitrajput901@gmail.com',

    url='https://github.com/Cargill-AI/coco-transform-util',
    keywords=['COCO', 'Computer Vision', 'Deep Learning'],

    # license= 'MIT', "Apache 2.0"
    # license="Apache 2.0",

    zip_safe=False,
    install_requires=install_requires,

    packages=find_packages(),

    include_package_data=True,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6', ],
)

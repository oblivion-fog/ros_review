from setuptools import find_packages, setup

package_name = 'exercise_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fog',
    maintainer_email='miwusenlin.g@qq.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tf_broadcaster = exercise_py.tf_broadcaster:main',
            'tf_listener = exercise_py.tf_listener:main',
            'tf_spawn = exercise_py.tf_spawn:main',
        ],
    },
)

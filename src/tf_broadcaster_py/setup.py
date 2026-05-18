from setuptools import find_packages, setup

package_name = 'tf_broadcaster_py'

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
            'static_tf_broadcaster_py = tf_broadcaster_py.static_tf_broadcaster_py:main',
            'dynamic_tf_broadcaster_py = tf_broadcaster_py.dynamic_tf_broadcaster_py:main',
            'tf_point_broadcaster_py = tf_broadcaster_py.tf_point_broadcaster_py:main',
        ],
    },
)

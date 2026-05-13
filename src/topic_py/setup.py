from setuptools import find_packages, setup

package_name = 'topic_py'

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
            'pub_1 = topic_py.pub_1:main',
            'sub_1 = topic_py.sub_1:main',
            'stu_pub = topic_py.stu_pub:main',
            'stu_sub = topic_py.stu_sub:main',
        ],
    },
)

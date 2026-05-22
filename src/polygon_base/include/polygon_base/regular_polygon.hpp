#ifndef POLYGON_BASE_REGULAR_POLYGON_HPP
#define POLYGON_BASE_REGULAR_POLYGON_HPP

namespace polygon_base
{
    class RegularPolygon
    {
            public:
            virtual void initialize(double side_length) = 0;  
            virtual double area()=0;
            /**
             * @brief 虚析构函数
             * 
             * 声明为虚析构函数是为了确保当通过基类指针删除派生类对象时，
             * 能够正确调用派生类的析构函数，避免内存泄漏。
             * 这是实现多态时的标准做法。
             */
            virtual ~RegularPolygon(){};

            protected:
            /**
             * @brief 保护级别构造函数
             * 
             * 将构造函数声明为 protected 是为了：
             * 1. 防止从外部直接实例化抽象基类对象
             * 2. 允许派生类调用此构造函数来初始化基类部分
             * 3. 符合抽象接口类的设计规范
             */
            RegularPolygon(){};
    }; //namespace polygon_base
}

#endif //POLYGON_BASE_REGULAR_POLYGON_HPP
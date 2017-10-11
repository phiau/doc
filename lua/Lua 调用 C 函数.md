## Lua 调用 C 函数 ##

- 参考文档：www.luachina.net 翻译组在 2005 年基于 Lua5.0 翻译的 《Lua程序设计.chm》
- 开发环境：
 - 操作系统：64 位 CentOS release 6.6 (Final)
 - Lua 版本：Lua 5.2.2
 - 编译器  ：GCC 4.4.7
 
任何在Lua中注册的函数必须有同样的原型，这个原型声明定义就是lua.h中的lua_CFunction：

`typedef int (*lua_CFunction) (lua_State *L);`

从C的角度来看，一个C函数接受单一的参数Lua state，返回一个表示返回值个数的数字。所以，函数在将返回值入栈之前不需要清理栈，函数返回之后，Lua自动的清除栈中返回结果下面的所有内容。

上代码前先了解下几个接口：

- `void lua_setglobal (lua_State *L, const char *name);`

Pops a value from the stack and sets it as the new value of global name.

弹出栈顶的值，并设置一个新的全局名。可见这个是为栈顶的值设置一个新的全局名，这个值这里没说必须是什么类型。

- void `lua_pushcfunction (lua_State *L, lua_CFunction f);`

Pushes a C function onto the stack. This function receives a pointer to a C function and pushes onto the stack a Lua value of type function that, when called, invokes the corresponding C function.

Any function to be registered in Lua must follow the correct protocol to receive its parameters and return its results (see lua_CFunction).

lua\_pushcfunction is defined as a macro:

`#define lua_pushcfunction(L,f)  lua_pushcclosure(L,f,0)`

把一个 C 函数压入栈顶。 `lua_pushcfuncion` 这个函数接收一个 C 函数指针，然后压入一个 Lua 函数类型的值进栈，当这个 Lua 函数被调用时，调用相应的 C 函数（这里翻译描述，觉得有点怪）。

所有被注册到 Lua 的 C 函数，都必须遵循正确的规则：接收参数然后返回结果（见 `lua_CFunction`）。

### 直接上代码 ###
#### C 代码 l\_26\_1.c ####
	#include <stdio.h>
	#include <lua.h>
	#include <lauxlib.h>
	
	static int l_add (lua_State *L) {
	    int a = lua_tonumber(L, -1);
	    int b = lua_tonumber(L, -2);
	    printf("a = %d, b = %d\n", a, b);
	    lua_pushnumber(L, a + b);
	    return 1;
	}
	
	int main(void) {
	    lua_State *L = luaL_newstate();
	    luaL_openlibs(L);
	
	    lua_pushcfunction(L, l_add);
	    lua_setglobal(L, "add");
	
	    luaL_dofile(L, "s_26_1.lua");
	    lua_close(L);
	}

#### Lua 代码 s\_26\_1.lua ####

`print(add(3, 7))`

运行结果

	a = 7, b = 3
	10

可以看出，`lua_tonumber` 这个接口得到值之后，是不会改变栈元素的。而 lua 脚本调用完 C 接口后 Lua 会自动把参数弹出栈。

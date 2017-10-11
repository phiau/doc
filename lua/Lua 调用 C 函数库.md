## Lua 调用 C 动态链接库 ##

- 参考文档：www.luachina.net 翻译组在 2005 年基于 Lua5.0 翻译的 《Lua程序设计.chm》
           [http://blog.csdn.net/ljhjason/article/details/28860633](http://blog.csdn.net/ljhjason/article/details/28860633)
- 开发环境：
 - 操作系统：64 位 CentOS release 6.6 (Final)
 - Lua 版本：Lua 5.2.2
 - 编译器  ：GCC 4.4.7

前面 Lua 调用 C 函数，是通过一个 global name 来调用的。如果有很多 C 函数，那么就得注册很多的 global name。首先会增加代码量，其实 Lua 在调用也有点不好管理。 Lua 在调用的时候，如果可以像 C++ 的命名空间那样，***.add 这样来调用，那看起来也舒心一点。

《Lua程序设计.chm》 在 26.2 中提到：当你打算使用C函数来扩展Lua的时候，即使你仅仅只想注册一个C函数，将你的C代码设计为一个库是个比较好的思想。

Lua5.0 中的 `luaL_openlib` 在 5.1 中被 `luaL_register` 替换了，见[http://www.lua.org/manual/5.1/manual.html#7.3](http://www.lua.org/manual/5.1/manual.html#7.3)，而到了 5.2 `luaL_register` 被弃用了，用了 `luaL_setfuncs` 代替，见 [http://www.lua.org/manual/5.2/manual.html#8.3](http://www.lua.org/manual/5.2/manual.html#8.3)

上代码前先了解下几个接口：

- `void luaL_setfuncs (lua_State *L, const luaL_Reg *l, int nup);`

Registers all functions in the array l (see `luaL_Reg`) into the table on the top of the stack (below optional upvalues, see next).

When nup is not zero, all functions are created sharing nup upvalues, which must be previously pushed on the stack on top of the library table. These values are popped from the stack after the registration.

把数组 l 里的所有函数注册到**栈顶**的**表**里（后面的是可选项，下见）。

如果 nup 不是空，所有的函数共享 nup upvalues，操作前必须压入一个 library table 进栈。这些值在注册好之后都会被移出栈。

- `void luaL_newlibtable (lua_State *L, const luaL_Reg l[]);`

Creates a new table with a size optimized to store all entries in the array l (but does not actually store them). It is intended to be used in conjunction with `luaL_setfuncs` (see `luaL_newlib`).

It is implemented as a macro. The array l must be the actual array, not a pointer to it.

创建一个新的 table 来存储数组 l 里面的所有元素（但是不是真正存储他们）。它的作用是和 `luaL_setfuncs` 一起使用（见`luaL_newlib`）

- `void luaL_newlib (lua_State *L, const luaL_Reg *l);`

Creates a new table and registers there the functions in list l. It is implemented as the following macro:
`(luaL_newlibtable(L,l), luaL_setfuncs(L,l,0))`

创建一个新的 table 然后注册列表 l 里面的函数。它的实现是一个宏定义。

### 直接上代码 ###
#### C 代码 l\_26\_2.c ####
	#include <lua.h>
	#include <lauxlib.h>
	
	static int add(lua_State *L) {
	    int a = lua_tonumber(L,1);
	    int b = lua_tonumber(L,2);
	    lua_pushnumber(L, a + b);
	    return 1;
	}
	
	static const struct luaL_Reg lib[] = {
	    {"add", add},
	    {NULL, NULL}
	};
	
	// 格式已经固定了，就是 luaopen_***，*** 是生成的动态库的名字，暂时不清楚为什么格式是这样
	int luaopen_libname(lua_State *L) {
	    luaL_newlib(L, lib);
	    return 1;
	}

编译动态库：`gcc l_26_2.c -fPIC -shared -o libname.so`

#### Lua 代码 s\_26\_2.lua ####
	m = require("libname")
	c = m.add(14, 11)
	print('the result is ' ..c)

#### 结果 ####
	[root]# lua s_26_2.lua 
	the result is 25

这里调用之前，需要 require，能不能像调用系统 print 那样，直接调用或者 libname.add 这样来调用。直接在 lua 脚本，暂时是不可以的，脚本肯定要从某个地方知道这个函数的。不要以 so 库来调用，可能可以。下面是 `lbaselib.c` 的 `luaopen_base` 函数实现：

	static const luaL_Reg base_funcs[] = {
      //...
	  {"print", luaB_print},
	  //...
	  {NULL, NULL}
	};

	LUAMOD_API int luaopen_base (lua_State *L) {
	  /* set global _G */
	  lua_pushglobaltable(L);
	  lua_pushglobaltable(L);
	  lua_setfield(L, -2, "_G");
	  /* open lib into global table */
	  luaL_setfuncs(L, base_funcs, 0);
	  lua_pushliteral(L, LUA_VERSION);
	  lua_setfield(L, -2, "_VERSION");  /* set global _VERSION */
	  return 1;
	}

`luaL_newlib` 是一个宏，定义为 `(luaL_newlibtable(L,l), luaL_setfuncs(L,l,0))`，上面的实现主要也是调用这两个接口，只不过 table 它用的是全局的 table。所以可以猜测，我们可以用 table 来实现 libname.add 这种形式的调用，libname 应该就是一个 table。

#### C 代码 l\_26\_2_notso.c ####
	#include <lua.h>
	#include <lauxlib.h>
	
	static int add(lua_State *L) {
	    int a = lua_tonumber(L,1);
	    int b = lua_tonumber(L,2);
	    lua_pushnumber(L, a + b);
	    return 1;
	}
	
	static const struct luaL_Reg lib[] = {
	    {"add", add},
	    {NULL, NULL}
	};

	int main(void) {
	    lua_State *L = luaL_newstate();
	    luaL_openlibs(L);

		lua_newtable(L);
		lua_setglobal(L, "libname");
		lua_getglobal(L, "libname");
		luaL_setfuncs(L, lib, 0);
		luaL_dofile(L, "l_26_2_notso.lua");
		
		lua_close(L);
	}

#### Lua 代码 s\_26\_2_notso.lua ####
	print(libname.add(2,3))

编译：`gcc -I /usr/local/include/ l_26_2_notso.c -lm -ldl -llua`
## User-Defined Types in C（C自定义类型） ##

- 参考文档：www.luachina.net 翻译组在 2005 年基于 Lua5.0 翻译的 《Lua程序设计.chm》   
           [http://www.jellythink.com/archives/587](http://www.jellythink.com/archives/587)
- 开发环境：
 - 操作系统：64 位 CentOS release 6.6 (Final)
 - Lua 版本：Lua 5.2.2
 - 编译器  ：GCC 4.4.7

应用场景：在 Lua 脚本中调用 C 接口，操作 C 定义的指针。如果只有前面的接口，应该很难实现。C 定义的接口要如何获得 Lua 调用传过来的指针参数，前面的都是 `lua_pushnumber`、`lua_pushnumber` 这些类型。所以应该有一个类似的接口，可以在 C 中获取 Lua 传过来的指针，该接口为`lua_touserdata`。

而这个指针指向的内存块，是由 Lua 管理，还是由 C 自己管理，貌似都可以。Lua 提供了 C 接口 `lua_newuserdata` 来分配内存，如果用这个接口，C 代码就不要去释放这个内存块了。

上代码前先了解下几个接口：

- `void *lua_newuserdata (lua_State *L, size_t size);`

This function allocates a new block of memory with the given size, pushes onto the stack a new full userdata with the block address, and returns this address. The host program can freely use this memory.

这个函数根据参数 size 分配一个新的内存块，然后压入一个新的 full userdata 来和内存块地址对应（这个翻译描述有点拗口），然后返回这个地址。宿主程序可以自由的使用这块内存。

- `void *lua_touserdata (lua_State *L, int index);`

If the value at the given index is a full userdata, returns its block address. If the value is a light userdata, returns its pointer. Otherwise, returns NULL.

如果 index 索引的是一个 full userdata，则返回它相应的内存块地址。如果是 light userdata，则返回指针。否则返回 nil。

### userdata 和 light data ###

暂时的理解就是 userdata 是由 Lua 管理内存，而 light data 是由宿主程序自己管理内存。

### 直接上代码 ###
#### C 代码 l\_28\_1.c ####

	#include <lua.h>
	#include <lualib.h>
	#include <lauxlib.h>
	
	typedef struct NumArray {
	    int size;
	    double values[1];
	} NumArray;
	
	static int newarray (lua_State *L) {
	    int n = luaL_checkint(L, 1);
	    size_t nbytes = sizeof(NumArray) + (n - 1) * sizeof(double);
	    NumArray *a = (NumArray *) lua_newuserdata(L, nbytes);
	    a->size = n;
	    return 1;
	}
	
	static int setarray (lua_State *L) {
	    NumArray *a  = (NumArray *) lua_touserdata(L, 1);
	    int index = luaL_checkint(L, 2);
	    double value = luaL_checknumber(L, 3);
	
	    luaL_argcheck(L, NULL != a, 1, "'array' expected");
	
	    luaL_argcheck(L, 1 <= index && index <= a->size, 2, "index out of range");
	
	    a->values[index - 1] = value;
	    return 0;
	}
	
	static int getarray (lua_State *L) {
	    NumArray *a = (NumArray *) lua_touserdata(L, 1);
	    int index = luaL_checkint(L, 2);
	
	    luaL_argcheck(L, NULL != a, 1, "'array' expected");
	
	    luaL_argcheck(L, 1 <= index && index <= a->size, 2, "index out of range");
	
	    lua_pushnumber(L, a->values[index-1]);
	    return 1;
	}
	
	static int getsize (lua_State *L) {
	    NumArray *a = (NumArray *) lua_touserdata(L, 1);
	
	    luaL_argcheck(L, NULL != a, 1, "'array' expected");
	
	    lua_pushnumber(L, a->size);
	    return 1;
	}
	
	static const struct luaL_Reg arraylib[] = {
	        {"new", newarray},
	        {"set", setarray},
	        {"get", getarray},
	        {"size", getsize},
	        {NULL, NULL}
	};
	
	// gcc l_28_1.c -fPIC -shared -o array.so
	int luaopen_array(lua_State *L) {
	    luaL_newlib(L, arraylib);
	    return 1;
	}


#### Lua 代码 s\_28\_1.lua ####

	array = require("array")
	a = array.new(100)
	print(a)
	print(array.size(a))
	for i=1, 100 do
	  array.set(a, i, 1/i)
	end
	
	print(array.get(a, 10))
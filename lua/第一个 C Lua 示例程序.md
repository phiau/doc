## 第一个 C Lua 示例程序 ##

- 参考文档：www.luachina.net 翻译组在 2005 年基于 Lua5.0 翻译的 《Lua程序设计.chm》
- 开发环境：
 - 操作系统：64 位 CentOS release 6.6 (Final)
 - Lua 版本：Lua 5.2.2
 - 编译器  ：GCC 4.4.7
 
**Lua5.0** 和 **Lua5.2** 部分接口存在差异，可以参考：[http://www.lua.org/manual/5.1/manual.html#7.3](http://www.lua.org/manual/5.1/manual.html#7.3) 和 [http://www.lua.org/manual/5.2/manual.html#8.3](http://www.lua.org/manual/5.2/manual.html#8.3)。个人能力有限，望指出错误，共同进步。


### 直接上代码 ###
	//l_24_1.c
	#include <stdio.h>
	#include <string.h>
	#include <lua.h>
	#include <lauxlib.h>
	#include <lualib.h>
	
	int main(void)
	{
	    char buff[256];
	    int error;
		//-------- 5.2 下面的几个函数已经不能用了 --------
	    //lua_State *L = lua_open();
		//luaopen_base(L);
	    //luaopen_table(L);
	    //luaopen_string(L);
	    //luaopen_math(L);
		//-------- end --------

	    lua_State *L = luaL_newstate();
	    luaL_openlibs(L);
	    
	    while(NULL != fgets(buff, sizeof(buff), stdin)) {
	        error = luaL_loadbuffer(L, buff, strlen(buff), "line") || lua_pcall(L, 0, 0, 0);
	        if(error) {
	            fprintf(stderr, "%s", lua_tostring(L, -1));
	            lua_pop(L, 1);
	        }
	    }
	    lua_close(L);
	    return 0;
	}

编译： `gcc -I /usr/local/include/ l_24_1.c -lm -ldl -llua`
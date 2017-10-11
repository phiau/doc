## Lua 栈的基本操作 ##

- 参考文档：www.luachina.net 翻译组在 2005 年基于 Lua5.0 翻译的 《Lua程序设计.chm》
- 开发环境：
 - 操作系统：64 位 CentOS release 6.6 (Final)
 - Lua 版本：Lua 5.2.2
 - 编译器  ：GCC 4.4.7

### Lua 栈的下标 ###

Lua 和 C 的交互都是发生在栈顶，所以结合 Lua 的接口说明来操作栈，就明朗一些.

![](http://i.imgur.com/BLVsLSZ.png)

### Lua 栈操作接口说明 ###
- 24.2.1 常规的压入栈接口，这几个接口都是把相应类型的值压入栈顶
 - `void lua_pushnil (lua_State *L);`
 - `void lua_pushboolean (lua_State *L, int bool);`
 - `void lua_pushnumber (lua_State *L, double n);`
 - `void lua_pushlstring (lua_State *L, const char *s,size_t length);`
 - `void lua_pushstring (lua_State *L, const char *s);`

- 24.2.2 查询元素，这几个接口都是查询**栈**指定**索引位置**上的值
 - `int lua_is... (lua_State *L, int index);`  //查询指定位置的值类型
 - `nt lua_toboolean (lua_State *L, int index);`
 - `double lua_tonumber (lua_State *L, int index);`
 - `const char * lua_tostring (lua_State *L, int index);`
 - `size_t lua_strlen (lua_State *L, int index);`

- 24.2.3 其他的栈操作
 - `int  lua_gettop (lua_State *L);`  //返回栈的元素个数，也就是栈顶的索引（下标）
 - `void lua_settop (lua_State *L, int index);`
 - `void lua_pushvalue (lua_State *L, int index);`
 - `void lua_remove (lua_State *L, int index);`
 - `void lua_insert (lua_State *L, int index);`
 - `void lua_replace (lua_State *L, int index); `

`lua_settop` 这个是把把栈顶的位置设为 index 这个位置，所以如果 index 超出原有栈顶，则新位置用 nil 值填充，index 比原有栈顶低，则新位置上面的元素弹出栈；

`lua_pushvalue` 这个是把 index 这个位置的值**拷贝**放到栈顶，所以原有位置的值不变，以前自以为是把原来的移到栈顶；

`lua_insert` 这个是把**栈顶**元素**移到**指定位置，所以这个位置上面的所有元素都会往上移动一个位置；

`lua_remove` 这个是把**移除**指定位置的元素，所以移动完之后，这个位置上面的元素就会坠落一个位置；

`lua_replace` 这个是先把**栈顶**元素弹出，并用这个值来替换指定位置（这个位置是弹出前的位置）的值；
### 直接上代码 ###

	#include <stdio.h>
	#include <lua.h>
	
	static void stackDump(lua_State *L) {
	    int i;
	    int top = lua_gettop(L);
	    for (i = 1; i <= top; ++i) {
	        int t = lua_type(L, i);
	        switch (t) {
	
	            case LUA_TSTRING:
	                printf("'%s'", lua_tostring(L, i));
	                break;
	
	            case LUA_TBOOLEAN:
	                printf(lua_toboolean(L, i) ? "true" : "false");
	                break;
	
	            case LUA_TNUMBER:
	                printf("%g", lua_tonumber(L, i));
	                break;
	
	            default:
	                printf("%s", lua_typename(L, t));
	                break;
	        }
	        printf("  ");
	    }
	    printf("\n");
	}
	
	int main(void) {
	    lua_State *L = luaL_newstate();
	    lua_pushboolean(L, 1); lua_pushnumber(L, 10);
	    lua_pushnil(L); lua_pushstring(L, "hello");
	    stackDump(L);
	
	    lua_pushvalue(L, -4); stackDump(L);
	
	    lua_replace(L, 3); stackDump(L);
	
	    lua_settop(L, 6); stackDump(L);
	
	    lua_remove(L, -3); stackDump(L);
	
	    lua_settop(L, -5); stackDump(L);
	
	    lua_close(L);
	    return 0;
	}

## Lua manual ##
- `int luaL_ref (lua_State *L, int t);`

Creates and returns a reference, in the table at index t, for the object at the top of the stack (and pops the object).

A reference is a unique integer key. As long as you do not manually add integer keys into table t, luaL_ref ensures the uniqueness of the key it returns. You can retrieve an object referred by reference r by calling `lua_rawgeti(L, t, r)`. Function `luaL_unref` frees a reference and its associated object.

If the object at the top of the stack is nil, luaL_ref returns the constant `LUA_REFNIL`. The constant `LUA_NOREF` is guaranteed to be different from any reference returned by `luaL_ref`.

在 index 位置上的 table 为栈顶对象创建并返回一个引用（然后弹出对象）。通俗易懂：就是把栈顶的对象，注册到位置在 t 的 table 这张表上。

这个引用是一个独一无二的整数。只要你不手动往 table t 里增加整数 key，`luaL_ref` 就可以保证返回的值是独一无二的。你可以通过这个引用 r 来调用 `lua_rawgeti(L, t, r)` 检索到对象。函数 `luaL_unref` 释放引用和关联的对象。 

如果栈顶位置上的 table 是空，`luaL_ref` 返回常量 `LUA_REFNIL`。常量 `LUA_NOREF` 保证和 `luaL_ref` 返回的任何索引不一样。
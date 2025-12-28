# AI 助力 Android 工程化实践：（二）Cursor Rules 构建团队级开发规范

*—— 从"AI 熵增"到"架构守门员"，让 AI 成为团队的标准化引擎*

---

## 1. 背景

### 1.1 团队开发中的规范缺失问题

在实际 Android 项目开发中，如果团队没有统一的开发规范，即使每个成员都按经验或工具生成代码，也会面临一系列问题：

- **代码风格不统一**  
  - 命名方式各异（camelCase、snake_case 混用）  
  - 架构模式不一致（MVVM、MVP、MVI 并存）  
  - 包结构随个人习惯不同，难以快速定位类  

- **代码质量不稳定**  
  - 注释缺失，维护成本高  
  - 错误处理不统一，边界条件考虑不全  
  - 逻辑实现不完整，需人工补充或重构  

- **知识/架构碎片化**  
  - 数据层封装方式不统一，模块间难以整合  
  - 依赖注入方式不一致，增加测试复杂度  
  - 状态管理混乱：LiveData、Flow、StateFlow 混用  

- **协作效率低**  
  - 接口签名、返回类型不统一，需频繁调整  
  - 重复实现相似功能，缺乏复用  
  - 整体代码整合和重构成本高  

- **技术迭代带来的挑战**  
  - 状态管理演进：LiveData → StateFlow → SharedFlow  
  - UI 框架变迁：XML → Jetpack Compose  
  - 依赖注入框架：Dagger → Koin → Hilt  
  - 异步处理方式：AsyncTask → RxJava → Coroutines  

如果缺少统一规范，团队开发的代码可能无法直接复用，需要大量手动修改，测试和调试成本高，整体项目维护难度大，协作效率明显下降。

### 1.2 解决方案：Cursor Rules

**Cursor Rules（`.cursorrules` 文件）** 是 Cursor IDE 提供的规则配置机制，它可以让 AI 在生成代码时遵循团队统一的技术栈、架构模式和编码规范。

通过 `.cursorrules`，我们可以：
1. **统一技术栈**：强制使用 StateFlow、Hilt、Compose 等现代技术
2. **规范架构模式**：统一 MVVM + Clean Architecture
3. **标准化代码风格**：命名规范、注释规范、错误处理规范
4. **提升生成质量**：确保生成的代码符合团队标准，可直接使用

> `.cursorrules` 就像是团队的"架构师"，在 AI 生成代码时自动把关，确保每一行代码都符合团队规范。

---

## 2. 实战对比：没有规则 vs 有规则

### 2.1 创建 `.cursorrules` 文件

1. **在项目根目录创建 `.cursorrules` 文件**
   - 文件名必须是 `.cursorrules`（注意前面的点）
   - 文件位置：项目根目录（与 `build.gradle` 同级）

2. **编写规则内容**
   - 使用 Markdown 格式编写规则
   - 规则应该清晰、具体、可执行
   - 可以参考第3章推荐的开源项目中的规则文件

3. **团队共享**
   - 将 `.cursorrules` 文件提交到 Git 仓库
   - 确保所有团队成员都使用相同的规则文件

### 2.2 场景：编写"用户详情" ViewModel

**需求**：写一个"用户详情"的 ViewModel，包含一个根据 ID 获取用户的方法。

### 2.3 没有 `.cursorrules` 的问题代码

在没有 `.cursorrules` 的情况下，AI 可能生成如下代码：

```kotlin
package com.example.demoapp.cursordemo

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.demoapp.architecture.mvvm.User
import com.example.demoapp.architecture.mvvm.UserRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 用户详情 ViewModel
 * 用于管理用户详情页面的数据和业务逻辑
 * 
 * @ProjectName: DemoApp
 * @Author: YangShuang
 * @Date: 2024/12/19
 */
class UserDetailViewModel : ViewModel() {
    // ❌ 问题 1：没有 Hilt 注入，你需要手动去改构造函数
    private val userRepository = UserRepository()
    
    // 用户详情数据
    private val _user = MutableLiveData<User?>()
    val user: LiveData<User?> = _user
    
    // 加载状态
    private val _isLoading = MutableLiveData<Boolean>()
    // ❌ 问题 2：还在用 LiveData，而你项目早就全切 Flow 了
    val isLoading: LiveData<Boolean> = _isLoading
    
    // 错误消息
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    /**
     * 根据 ID 获取用户信息
     * 
     * @param userId 用户 ID
     */
    fun getUserById(userId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            
            try {
                val user = withContext(Dispatchers.IO) {
                    userRepository.getUserInfo(userId)
                }
                // ❌ 问题 3：简单的 try-catch，没有处理你项目定义的 Result 封装
                if (user != null) {
                    _user.value = user
                } else {
                    _errorMessage.value = "用户不存在"
                }
                
            } catch (e: Exception) {
                _errorMessage.value = "获取用户信息失败: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
    
    /**
     * 清除错误消息
     */
    fun clearError() {
        _errorMessage.value = null
    }
}
```

这段代码存在几个明显问题：

1. **缺少 Hilt 依赖注入**（对应问题 1）：直接 `new UserRepository()`，后续想写单元测试都难，还得手动改构造函数。
2. **使用了过时的 LiveData**（对应问题 2）：项目早就切换到 Flow 了，这里还在用 LiveData，状态管理方式不一致。
3. **错误处理不规范**（对应问题 3）：简单的 try-catch，没有用项目统一的 Result 封装，错误处理逻辑分散。

拿到这样的代码，你基本不能直接用。得手动加上 `@HiltViewModel`，把三个 `LiveData` 改成统一的 `StateFlow`，把 `UserRepository` 改成构造函数注入，还要重构错误处理逻辑。一套改下来，半小时就没了。

### 2.4 有了 `.cursorrules` 的改进代码

**前提**：项目根目录有 `.cursorrules`，内容如下：

```markdown
# .cursorrules for Android

1. **技术栈**：始终使用 Kotlin, Jetpack Compose, Hilt, Coroutines.
2. **状态管理**：必须使用 `StateFlow` 和 `SharedFlow`，严禁使用 `LiveData`。
3. **依赖注入**：ViewModel 必须使用 `@HiltViewModel` 和 `@Inject` 构造函数。
4. **UI状态**：ViewModel 必须暴露一个 `uiState` (data class) 而不是零散的变量。
5. **并发**：网络请求必须使用 `viewModelScope` 并在 IO Dispatcher 中运行。
```

**你的指令（完全一样）**：
> "写一个 UserDetailViewModel，包含一个根据 ID 获取用户的方法。"

**AI 生成的代码**：

```kotlin
package com.example.demoapp.cursordemo

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import javax.inject.Inject

/**
 * 用户详情 ViewModel
 *
 * @ProjectName: DemoApp
 * @Desc: 管理用户详情页面的 UI 状态和数据
 * @Author: YangShuang
 */
// ✅ 亮点 1：符合 Hilt 规范
// 使用 @HiltViewModel 注解，无需手动在 Activity/Fragment 中通过 ViewModelFactory 创建实例
@HiltViewModel
class UserDetailViewModel @Inject constructor(
    // ✅ 亮点 2：依赖注入 (DI)
    // 构造函数注入 Repository，解耦数据层，方便单元测试 (Mock Repository)
    private val userRepository: UserRepository
) : ViewModel() {
    
    // ✅ 亮点 3：现代状态管理 (StateFlow vs LiveData)
    // 使用 MutableStateFlow 替代过时的 LiveData，天然支持协程，并且初始值必须非空
    private val _uiState = MutableStateFlow(UserDetailUiState())
    
    // ✅ 亮点 4：单一数据源与安全性 (Backing Property)
    // 对外只暴露不可变的 StateFlow，防止外部 View 层意外修改状态
    val uiState: StateFlow<UserDetailUiState> = _uiState.asStateFlow()
    
    /**
     * 根据 ID 获取用户信息
     * @param userId 用户 ID
     */
    fun getUserById(userId: Int) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, error = null)
            
            try {
                // ✅ 亮点 7：线程调度
                // 显式切换到 IO Dispatcher 处理数据库/网络操作，确保不阻塞主线程 (Main Thread)
                val user = withContext(Dispatchers.IO) {
                    userRepository.getUserById(userId)
                }
                
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    user = user,
                    error = if (user == null) "用户不存在" else null
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = "获取用户信息失败: ${e.message}"
                )
            }
        }
    }
}

/**
 * 用户详情 UI 状态
 */
data class UserDetailUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)
```

**改进总结**：
1. ✅ **Hilt 依赖注入**：使用 `@HiltViewModel` 和构造函数注入，符合现代 Android 开发规范
2. ✅ **StateFlow 状态管理**：使用 `StateFlow` 替代 `LiveData`，天然支持协程
3. ✅ **统一 UI 状态**：使用 `data class` 封装所有 UI 状态，单一数据源
4. ✅ **线程安全**：使用 `Dispatchers.IO` 处理网络请求，不阻塞主线程
5. ✅ **代码可直接使用**：生成的代码完全符合项目规范，无需修改

> 在 Android 这种新旧代码共存的领域，`.cursorrules` 不仅能防止 AI 写出"三年前"的代码，更是团队架构规范的自动化守门员。

---

## 3. 推荐开源项目：cursor-rules

https://github.com/flyeric0212/cursor-rules

该项目整理了来自不同项目的 Cursor 规则文件，提供多种编程语言和框架的规则支持，目前已有 1.5k+ stars，社区活跃度高。

该项目采用分层结构组织规则：基础规则层（core、tech-stack、project-structure）、编程语言层（Kotlin、Java、TypeScript 等）、框架层（Android、React、Vue、Flutter 等）以及其他工具层（Git、文档等）。对于 Android 开发者来说，项目中的 `frameworks/android.mdc` 和 `languages/kotlin.mdc` 是最常用的规则文件。

项目结构如下：

```
cursor-rules/
├── base/                    # 基础规则层（通用规则）
│   ├── core.mdc             # 核心开发原则和响应语言
│   ├── tech-stack.mdc       # 技术栈定义和官方文档链接
│   ├── project-structure.mdc # 项目结构和文件组织规范
│   └── general.mdc          # 通用编程规则
├── languages/               # 编程语言特定规则
│   ├── c++.mdc              # C++语言规则
│   ├── css.mdc              # CSS样式规则
│   ├── golang.mdc           # Go语言规则
│   ├── java.mdc             # Java语言规则
│   ├── kotlin.mdc           # Kotlin语言规则
│   ├── python.mdc           # Python语言规则
│   ├── typescript.mdc       # TypeScript语言规则
│   ├── wxml.mdc             # 微信小程序标记语言规则
│   └── wxss.mdc             # 微信小程序样式表规则
├── frameworks/              # 框架相关规则
│   ├── # 前端框架
│   ├── nextjs.mdc           # Next.js框架规则
│   ├── react.mdc            # React框架规则
│   ├── react-hook-form.mdc  # React Hook Form规则
│   ├── react-native.mdc     # React Native框架规则
│   ├── shadcn.mdc           # Shadcn UI规则
│   ├── tailwind.mdc         # Tailwind CSS规则
│   ├── vuejs.mdc            # Vue.js框架规则
│   ├── zod.mdc              # Zod验证规则
│   ├── zustand.mdc          # Zustand状态管理规则
│   ├── # 后端框架
│   ├── django.mdc           # Django框架规则
│   ├── fastapi.mdc          # FastAPI框架规则
│   ├── flask.mdc            # Flask框架规则
│   ├── springboot.mdc       # Spring Boot框架规则
│   ├── # 移动开发框架
│   ├── android.mdc          # Android框架规则
│   ├── android_bak.mdc      # Android框架规则（备份版本）
│   ├── flutter.mdc          # Flutter框架规则
│   └── swiftui.mdc          # SwiftUI框架规则
├── other/                   # 其他工具层规则
│   ├── document.mdc         # 文档编写规则
│   ├── git.mdc              # Git相关规则
│   └── gitflow.mdc          # Git Flow工作流规则
└── demo/                    # 示例配置
    ├── python/              # Python项目示例配置
    └── vue/                 # Vue项目示例配置
```

---

## 4. 相关资源

- [Cursor 官方文档](https://cursor.sh/docs)
- [Cursor Rules 最佳实践](https://cursor.sh/docs/cursor-rules)
- [Kotlin 编码规范](https://kotlinlang.org/docs/coding-conventions.html)
- [Android 架构指南](https://developer.android.com/topic/architecture)

---

*本文是"AI 助力 Android 工程化实践"系列的第二篇，后续将分享更多 AI 在 Android 开发中的应用实践，敬请期待。*


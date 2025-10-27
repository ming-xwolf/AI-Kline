"""
MinIO 对象存储集成模块
参考 mcp-echarts 模块的 MinIO 集成实现
"""
import os
import logging
import tempfile
import asyncio
import concurrent.futures
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# 尝试导入 MinIO 客户端
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = None


def is_minio_configured() -> bool:
    """检查 MinIO 是否已配置"""
    if not MINIO_AVAILABLE:
        return False
    
    return bool(
        os.getenv('MINIO_ACCESS_KEY') and
        os.getenv('MINIO_SECRET_KEY') and
        os.getenv('MINIO_ENDPOINT')
    )


def get_minio_client() -> Optional[Minio]:
    """获取 MinIO 客户端实例"""
    if not is_minio_configured():
        return None
    
    try:
        endpoint = os.getenv('MINIO_ENDPOINT', 'localhost')
        access_key = os.getenv('MINIO_ACCESS_KEY')
        secret_key = os.getenv('MINIO_SECRET_KEY')
        
        use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
        port = int(os.getenv('MINIO_PORT', '9000'))
        
        client = Minio(
            f"{endpoint}:{port}",
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl
        )
        
        return client
    except Exception as e:
        logger.warning(f"创建 MinIO 客户端失败: {e}")
        return None


async def store_html_to_minio(html_content: str, filename_prefix: str = "chart") -> Optional[str]:
    """
    将 HTML 内容存储到 MinIO 并返回 URL
    
    Args:
        html_content: HTML 内容字符串
        filename_prefix: 文件名前缀
    
    Returns:
        如果成功返回 URL，否则返回 None
    """
    if not is_minio_configured():
        return None
    
    client = get_minio_client()
    if not client:
        return None
    
    try:
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{filename_prefix}_{timestamp}.html"
        object_name = f"charts/{filename}"
        bucket_name = os.getenv('MINIO_BUCKET_NAME', 'ai-kline-charts')
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(html_content)
            tmp_file_path = tmp_file.name
        
        try:
            # 确保 bucket 存在
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"创建 MinIO bucket: {bucket_name}")
            
            # 上传文件到 MinIO
            client.fput_object(
                bucket_name,
                object_name,
                tmp_file_path,
                content_type='text/html'
            )
            
            logger.info(f"上传文件到 MinIO: {object_name}")
            
            # 生成访问 URL
            # 优先使用外部访问地址（MINIO_EXTERNAL_ENDPOINT），如果没有则使用内部地址
            external_endpoint = os.getenv('MINIO_EXTERNAL_ENDPOINT')
            external_port = os.getenv('MINIO_EXTERNAL_PORT')
            
            if external_endpoint:
                endpoint = external_endpoint
                port = external_port if external_port else os.getenv('MINIO_PORT', '9000')
            else:
                endpoint = os.getenv('MINIO_ENDPOINT', 'localhost')
                port = os.getenv('MINIO_PORT', '9000')
            
            use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
            protocol = 'https' if use_ssl else 'http'
            
            url = f"{protocol}://{endpoint}:{port}/{bucket_name}/{object_name}"
            
            return url
            
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass
                
    except Exception as e:
        logger.warning(f"MinIO 存储失败，回退到本地: {e}")
        return None


async def store_image_to_minio(image_base64: str, filename_prefix: str = "chart", content_type: str = 'image/png') -> Optional[str]:
    """
    将图片（base64）存储到 MinIO 并返回 URL
    
    Args:
        image_base64: Base64 编码的图片数据
        filename_prefix: 文件名前缀
        content_type: 内容类型（image/png 或 image/svg+xml）
    
    Returns:
        如果成功返回 URL，否则返回 None
    """
    if not is_minio_configured():
        return None
    
    client = get_minio_client()
    if not client:
        return None
    
    try:
        import base64
        
        # 确定文件扩展名和内容类型
        ext = '.png' if 'image/png' in content_type else '.svg'
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{filename_prefix}_{timestamp}{ext}"
        object_name = f"charts/{filename}"
        bucket_name = os.getenv('MINIO_BUCKET_NAME', 'ai-kline-charts')
        
        # 创建临时文件
        if ext == '.png':
            # PNG: base64 解码为二进制
            image_bytes = base64.b64decode(image_base64)
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name
        else:
            # SVG: 如果也是 base64，需要解码；否则直接写入字符串
            try:
                image_bytes = base64.b64decode(image_base64)
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                    tmp_file.write(image_bytes)
                    tmp_file_path = tmp_file.name
            except:
                # 如果不是 base64，直接写入字符串
                with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as tmp_file:
                    tmp_file.write(image_base64)
                    tmp_file_path = tmp_file.name
        
        try:
            # 确保 bucket 存在
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
                logger.info(f"创建 MinIO bucket: {bucket_name}")
            
            # 上传文件到 MinIO
            client.fput_object(
                bucket_name,
                object_name,
                tmp_file_path,
                content_type=content_type
            )
            
            logger.info(f"上传图片到 MinIO: {object_name}")
            
            # 生成访问 URL
            external_endpoint = os.getenv('MINIO_EXTERNAL_ENDPOINT')
            external_port = os.getenv('MINIO_EXTERNAL_PORT')
            
            if external_endpoint:
                endpoint = external_endpoint
                port = external_port if external_port else os.getenv('MINIO_PORT', '9000')
            else:
                endpoint = os.getenv('MINIO_ENDPOINT', 'localhost')
                port = os.getenv('MINIO_PORT', '9000')
            
            use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
            protocol = 'https' if use_ssl else 'http'
            
            url = f"{protocol}://{endpoint}:{port}/{bucket_name}/{object_name}"
            
            return url
            
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass
                
    except Exception as e:
        logger.warning(f"MinIO 图片存储失败: {e}")
        return None


async def store_file_to_minio(file_path: str, object_name: str, content_type: str = 'text/html') -> Optional[str]:
    """
    将本地文件上传到 MinIO 并返回 URL
    
    Args:
        file_path: 本地文件路径
        object_name: MinIO 对象名称
        content_type: 内容类型
    
    Returns:
        如果成功返回 URL，否则返回 None
    """
    if not is_minio_configured():
        return None
    
    client = get_minio_client()
    if not client:
        return None
    
    try:
        bucket_name = os.getenv('MINIO_BUCKET_NAME', 'ai-kline-charts')
        
        # 确保 bucket 存在
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"创建 MinIO bucket: {bucket_name}")
        
        # 上传文件到 MinIO
        client.fput_object(
            bucket_name,
            object_name,
            file_path,
            content_type=content_type
        )
        
        logger.info(f"上传文件到 MinIO: {object_name}")
        
        # 生成访问 URL
        endpoint = os.getenv('MINIO_ENDPOINT', 'localhost')
        port = os.getenv('MINIO_PORT', '9000')
        use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
        protocol = 'https' if use_ssl else 'http'
        
        url = f"{protocol}://{endpoint}:{port}/{bucket_name}/{object_name}"
        
        return url
        
    except Exception as e:
        logger.warning(f"MinIO 存储失败: {e}")
        return None


class MinIOStorageManager:
    """
    MinIO 存储管理器
    提供同步和异步方法处理 MinIO 存储操作
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def is_configured(self) -> bool:
        """检查 MinIO 是否已配置"""
        return is_minio_configured()
    
    def get_client(self):
        """获取 MinIO 客户端"""
        return get_minio_client()
    
    async def upload_image(self, image_base64: str, filename_prefix: str = "chart", content_type: str = 'image/png', timeout: int = 30) -> Optional[str]:
        """
        上传图片（base64）到 MinIO（异步方法）
        
        Args:
            image_base64: Base64 编码的图片数据
            filename_prefix: 文件名前缀
            content_type: 内容类型
            timeout: 超时时间（秒）
        
        Returns:
            如果成功返回 URL，否则返回 None
        """
        if not is_minio_configured():
            self.logger.debug("MinIO 未配置，跳过上传")
            return None
        
        try:
            url = await store_image_to_minio(image_base64, filename_prefix, content_type)
            return url
        except Exception as e:
            self.logger.warning(f"MinIO 上传失败: {e}")
            return None
    
    def upload_image_sync(self, image_base64: str, filename_prefix: str = "chart", content_type: str = 'image/png', timeout: int = 30) -> Optional[str]:
        """
        上传图片（base64）到 MinIO（同步方法）
        
        此方法可以在同步函数中安全调用异步函数，使用线程池处理事件循环问题
        
        Args:
            image_base64: Base64 编码的图片数据
            filename_prefix: 文件名前缀
            content_type: 内容类型
            timeout: 超时时间（秒）
        
        Returns:
            如果成功返回 URL，否则返回 None
        """
        if not is_minio_configured():
            self.logger.debug("MinIO 未配置，跳过上传")
            return None
        
        def run_in_new_loop():
            """在新的事件循环中运行异步函数"""
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(store_image_to_minio(image_base64, filename_prefix, content_type))
                finally:
                    new_loop.close()
            except Exception as e:
                self.logger.error(f"MinIO 上传失败: {e}")
                return None
        
        try:
            # 在独立线程中执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                url = future.result(timeout=timeout)
                return url
        except concurrent.futures.TimeoutError:
            self.logger.error(f"MinIO 上传超时（>{timeout}秒）")
            return None
        except Exception as e:
            self.logger.warning(f"MinIO 上传失败: {e}")
            return None
    
    async def upload_html(self, html_content: str, filename_prefix: str = "chart", timeout: int = 30) -> Optional[str]:
        """
        上传 HTML 内容到 MinIO（异步方法）
        
        Args:
            html_content: HTML 内容字符串
            filename_prefix: 文件名前缀
            timeout: 超时时间（秒）
        
        Returns:
            如果成功返回 URL，否则返回 None
        """
        if not is_minio_configured():
            self.logger.debug("MinIO 未配置，跳过上传")
            return None
        
        try:
            url = await store_html_to_minio(html_content, filename_prefix)
            return url
        except Exception as e:
            self.logger.warning(f"MinIO 上传失败: {e}")
            return None
    
    def upload_html_sync(self, html_content: str, filename_prefix: str = "chart", timeout: int = 30) -> Optional[str]:
        """
        上传 HTML 内容到 MinIO（同步方法）
        
        此方法可以在同步函数中安全调用异步函数，使用线程池处理事件循环问题
        
        Args:
            html_content: HTML 内容字符串
            filename_prefix: 文件名前缀
            timeout: 超时时间（秒）
        
        Returns:
            如果成功返回 URL，否则返回 None
        """
        if not is_minio_configured():
            self.logger.debug("MinIO 未配置，跳过上传")
            return None
        
        def run_in_new_loop():
            """在新的事件循环中运行异步函数"""
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(store_html_to_minio(html_content, filename_prefix))
                finally:
                    new_loop.close()
            except Exception as e:
                self.logger.error(f"MinIO 上传失败: {e}")
                return None
        
        try:
            # 在独立线程中执行
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                url = future.result(timeout=timeout)
                return url
        except concurrent.futures.TimeoutError:
            self.logger.error(f"MinIO 上传超时（>{timeout}秒）")
            return None
        except Exception as e:
            self.logger.warning(f"MinIO 上传失败: {e}")
            return None
    
    def get_url_from_object(self, object_name: str) -> str:
        """
        根据对象名称生成访问 URL
        
        Args:
            object_name: MinIO 对象名称
        
        Returns:
            访问 URL
        """
        endpoint = os.getenv('MINIO_ENDPOINT', 'localhost')
        port = os.getenv('MINIO_PORT', '9000')
        use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
        bucket_name = os.getenv('MINIO_BUCKET_NAME', 'ai-kline-charts')
        
        protocol = 'https' if use_ssl else 'http'
        url = f"{protocol}://{endpoint}:{port}/{bucket_name}/{object_name}"
        
        return url
    
    def ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> bool:
        """
        确保存储桶存在
        
        Args:
            bucket_name: 存储桶名称，默认为配置的存储桶
        
        Returns:
            如果存储桶存在或创建成功返回 True，否则返回 False
        """
        if not is_minio_configured():
            return False
        
        client = get_minio_client()
        if not client:
            return False
        
        try:
            bucket = bucket_name or os.getenv('MINIO_BUCKET_NAME', 'ai-kline-charts')
            
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                self.logger.info(f"创建 MinIO bucket: {bucket}")
            else:
                self.logger.debug(f"MinIO bucket 已存在: {bucket}")
            
            return True
        except Exception as e:
            self.logger.error(f"确保 bucket 存在失败: {e}")
            return False


# 创建全局实例
minio_storage_manager = MinIOStorageManager()


"""
AI-Kline 图片生成模块
基于ECharts配置生成PNG/SVG图片
"""

import base64
import json
import os
import tempfile
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

# FastMCP Content types
try:
    from mcp.server.models import Image
    MCP_IMAGE_AVAILABLE = True
except ImportError:
    try:
        from mcp.types import Image
        MCP_IMAGE_AVAILABLE = True
    except ImportError:
        MCP_IMAGE_AVAILABLE = False
        logger.warning("Could not import MCP Image type")

# 默认保存路径常量
DEFAULT_SAVE_PATH = "./output/charts"

class ImageGenerator:
    """
    图片生成器类，负责将ECharts配置转换为图片
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.save_path = DEFAULT_SAVE_PATH
    
    def generate_chart_image(
        self,
        echarts_option: Dict[str, Any],
        width: int = 800,
        height: int = 600,
        theme: str = "default",
        output_type: str = "png",
        tool_name: str = "unknown",
        stock_code: str = "",
        indicators: str = ""
    ) -> str:
        """
        生成图表图片
        
        参数:
            echarts_option (dict): ECharts配置选项
            width (int): 图片宽度，默认800
            height (int): 图片高度，默认600
            theme (str): 主题，默认'default'
            output_type (str): 输出类型，'png'或'svg'，默认'png'
            tool_name (str): 工具名称，用于调试日志
            
        返回:
            str: 
                - PNG: base64编码的图片数据
                - SVG: SVG字符串（未编码）
        """
        try:
            # 动态调整图片高度
            if height is None:
                # 计算子图数量
                subplot_count = len(echarts_option.get('grid', []))
                
                # 参考visualizer.py的动态高度计算逻辑
                # base_height = 500  # 基础高度，确保X轴完全显示
                # chart_height = 350  # 每个图表的高度
                # dynamic_height = base_height + (subplot_count * chart_height)
                
                # 转换为百分比计算（基于800px基准）
                base_height_px = 500  # 基础高度500px
                chart_height_px = 350  # 每个图表高度350px
                
                # 总高度 = 基础高度 + (子图数量 × 每个图表高度)
                dynamic_height_px = base_height_px + (subplot_count * chart_height_px)
                
                # 转换为像素高度
                height = dynamic_height_px
                
                logger.debug(f"[DEBUG] {tool_name} 动态调整图片高度: {height}px (子图数量: {subplot_count}, 基础高度: {base_height_px}px, 图表高度: {chart_height_px}px)")
            
            logger.debug(f"[DEBUG] {tool_name} 生成图表: width={width}, height={height}, theme={theme}, output_type={output_type}")
            
            if output_type == "svg":
                return self._generate_svg(echarts_option, width, height, theme, stock_code, indicators)
            elif output_type == "png":
                return self._generate_png(echarts_option, width, height, theme, stock_code, indicators)
            else:
                raise ValueError(f"不支持的输出类型: {output_type}")
                
        except Exception as error:
            logger.error(f"[ERROR] {tool_name} 图表生成失败: {error}")
            raise Exception(f"图表渲染失败: {str(error)}")
    
    def _generate_svg(self, echarts_option: Dict[str, Any], width: int, height: int, theme: str, stock_code: str = "", indicators: str = "") -> str:
        """
        生成SVG格式的图表并保存到本地，返回SVG字符串
        """
        try:
            # 使用selenium + chrome headless生成SVG
            svg_content = self._render_with_selenium(echarts_option, width, height, theme, "svg")
            
            # 保存SVG文件到本地
            local_file_path = self._save_svg_to_local(svg_content, stock_code, indicators)
            
            # 直接返回SVG字符串，不进行base64编码
            return svg_content
        except Exception as e:
            logger.error(f"SVG生成失败: {e}")
            raise
    
    def _generate_png(self, echarts_option: Dict[str, Any], width: int, height: int, theme: str, stock_code: str = "", indicators: str = "") -> str:
        """
        生成PNG格式的图表并保存到本地，返回base64编码的字符串
        """
        try:
            # 使用selenium + chrome headless生成PNG
            png_base64 = self._render_with_selenium(echarts_option, width, height, theme, "png")
            
            # 保存PNG文件到本地
            local_file_path = self._save_png_to_local(png_base64, stock_code, indicators)
            
            return png_base64
        except Exception as e:
            logger.error(f"PNG生成失败: {e}")
            raise
    
    def _render_with_selenium(self, echarts_option: Dict[str, Any], width: int, height: int, theme: str, output_format: str) -> str:
        """
        使用Selenium和Chrome headless渲染图表
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
            
            # 创建Chrome选项
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # 使用新的 headless 模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--window-size={width},{height}")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # 检测Chrome二进制位置（支持ARM64和AMD64）
            chrome_binaries = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]
            chrome_binary_location = None
            for binary in chrome_binaries:
                if os.path.exists(binary):
                    chrome_binary_location = binary
                    break
            
            if chrome_binary_location:
                chrome_options.binary_location = chrome_binary_location
            
            # 创建临时HTML文件
            html_content = self._create_html_template(echarts_option, width, height, theme, output_format)
            temp_html_path = os.path.join(self.temp_dir, f"chart_{int(time.time())}.html")
            
            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            driver = None
            try:
                # 启动Chrome - 在Docker环境中使用service参数
                from selenium.webdriver.chrome.service import Service
                
                # 尝试使用环境变量中的chromedriver路径，如果不存在则使用默认路径
                chromedriver_paths = [
                    os.environ.get('CHROMEDRIVER_PATH'),
                    '/usr/local/bin/chromedriver',
                    '/usr/bin/chromedriver'
                ]
                
                chromedriver_path = None
                for path in chromedriver_paths:
                    if path and os.path.exists(path):
                        chromedriver_path = path
                        break
                
                if chromedriver_path:
                    service = Service(chromedriver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # 如果没有找到chromedriver，尝试自动查找
                    driver = webdriver.Chrome(options=chrome_options)
                
                driver.get(f"file://{temp_html_path}")
                
                # 等待图表渲染完成
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "chart"))
                )
                
                # 等待额外时间确保图表完全渲染
                time.sleep(2)
                
                if output_format == "svg":
                    # 获取SVG内容 - 使用JavaScript提取纯SVG
                    svg_content = driver.execute_script("""
                        var chartDiv = document.getElementById('chart');
                        var svgElement = chartDiv.querySelector('svg');
                        return svgElement ? svgElement.outerHTML : '';
                    """)
                    if not svg_content:
                        # 如果找不到SVG，回退到获取整个div
                        svg_element = driver.find_element(By.ID, "chart")
                        svg_content = svg_element.get_attribute("outerHTML")
                    return svg_content
                else:
                    # 获取PNG base64 - 等待Canvas元素出现
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "echarts-canvas"))
                    )
                    
                    canvas_element = driver.find_element(By.ID, "echarts-canvas")
                    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').split(',')[1];", canvas_element)
                    return canvas_base64
                    
            finally:
                if driver:
                    driver.quit()
                # 清理临时文件
                if os.path.exists(temp_html_path):
                    os.remove(temp_html_path)
                    
        except ImportError:
            logger.error("Selenium未安装，请运行: pip install selenium")
            raise Exception("Selenium未安装，无法生成图片")
        except Exception as e:
            logger.error(f"Selenium渲染失败: {e}")
            raise Exception(f"图片渲染失败: {str(e)}")
    
    def _create_html_template(self, echarts_option: Dict[str, Any], width: int, height: int, theme: str, output_format: str) -> str:
        """
        创建HTML模板用于Selenium渲染
        """
        echarts_config_json = json.dumps(echarts_option, ensure_ascii=False, indent=2)
        
        if output_format == "svg":
            # SVG模式使用SVG渲染器
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ECharts Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #chart {{ width: {width}px; height: {height}px; }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        var chart = echarts.init(document.getElementById('chart'), '{theme}', {{
            renderer: 'svg',
            width: {width},
            height: {height}
        }});
        
        var option = {echarts_config_json};
        chart.setOption(option);
        
        // 禁用动画
        chart.setOption({{
            animation: false
        }});
    </script>
</body>
</html>
"""
        else:
            # PNG模式使用Canvas渲染器
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ECharts Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #chart {{ width: {width}px; height: {height}px; }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        var chart = echarts.init(document.getElementById('chart'), '{theme}', {{
            renderer: 'canvas',
            width: {width},
            height: {height}
        }});
        
        var option = {echarts_config_json};
        chart.setOption(option);
        
        // 禁用动画
        chart.setOption({{
            animation: false
        }});
        
        // 等待图表渲染完成后，将Canvas转换为图片
        setTimeout(function() {{
            var canvas = document.getElementById('chart').querySelector('canvas');
            if (canvas) {{
                canvas.id = 'echarts-canvas';
            }}
        }}, 1000);
    </script>
</body>
</html>
"""
        
        return html_template
    
    def convert_echarts_option_to_candlestick_format(self, stock_data, indicators, stock_code, requested_indicators, frequency="daily"):
        """
        将AI-Kline的ECharts配置转换为candlestick格式
        参考mcp-echarts的candlestick.ts实现
        """
        try:
            # 准备数据
            dates = stock_data['date'].dt.strftime('%Y-%m-%d').tolist()
            ohlc_data = [[float(stock_data['open'].iloc[i]), 
                         float(stock_data['close'].iloc[i]), 
                         float(stock_data['low'].iloc[i]), 
                         float(stock_data['high'].iloc[i])] for i in range(len(stock_data))]
            
            # 获取股票名称
            stock_name = self._get_stock_name(stock_code)
            
            # 获取频率显示
            frequency_display = self._get_frequency_display(frequency)
            
            # 构建ECharts配置
            echarts_option = {
                "animation": False,
                "legend": {
                    "top": "6%",
                    "left": "center",
                    "data": ["K线"],
                    "orient": "horizontal",
                    "itemGap": 15,
                    "textStyle": {
                        "fontSize": 10
                    },
                    "type": "scroll"
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "cross"
                    },
                    "borderWidth": 1,
                    "borderColor": "#ccc",
                    "padding": 10,
                    "textStyle": {
                        "color": "#000"
                    }
                },
                "xAxis": [
                    {
                        "type": "category",
                        "data": dates,
                        "boundaryGap": True,
                        "axisLine": {"onZero": False},
                        "splitLine": {"show": False},
                        "min": -0.2,
                        "max": len(dates) - 0.8
                    }
                ],
                "yAxis": [
                    {
                        "scale": True,
                        "splitArea": {
                            "show": True
                        }
                    }
                ],
                "grid": [
                    {
                        "left": "12%",
                        "right": "10%",
                        "top": "12%",
                        "bottom": "15%"
                    }
                ],
                "series": [
                    {
                        "name": "K线",
                        "type": "candlestick",
                        "data": ohlc_data,
                        "itemStyle": {
                            "color": "#ef232a",
                            "color0": "#14b143",
                            "borderColor": "#ef232a",
                            "borderColor0": "#14b143"
                        },
                        "emphasis": {
                            "itemStyle": {
                                "color": "#ef232a",
                                "color0": "#14b143",
                                "borderColor": "#ef232a",
                                "borderColor0": "#14b143"
                            }
                        }
                    }
                ],
                "title": {
                    "left": "center",
                    "text": f"{stock_name}({stock_code}) {frequency_display}K线图"
                }
            }
            
            # 更新图例数据
            legend_data = ["K线"]
            
            # 添加技术指标
            if "MA" in requested_indicators:
                # 添加MA线
                echarts_option["series"].extend([
                    {
                        "name": "MA5",
                        "type": "line",
                        "data": indicators['MA5'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#FF6B6B"}
                    },
                    {
                        "name": "MA10",
                        "type": "line",
                        "data": indicators['MA10'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#4ECDC4"}
                    },
                    {
                        "name": "MA20",
                        "type": "line",
                        "data": indicators['MA20'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#45B7D1"}
                    },
                    {
                        "name": "MA30",
                        "type": "line",
                        "data": indicators['MA30'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#96CEB4"}
                    }
                ])
                legend_data.extend(["MA5", "MA10", "MA20", "MA30"])
            
            # 添加布林带
            if "BOLL" in requested_indicators:
                echarts_option["series"].extend([
                    {
                        "name": "BOLL上轨",
                        "type": "line",
                        "data": indicators['BOLL_upper'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#ef232a", "type": "dashed"}  # 上轨红色
                    },
                    {
                        "name": "BOLL中轨",
                        "type": "line",
                        "data": indicators['BOLL_middle'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#87CEEB", "type": "dashed"}  # 与上下轨一致使用虚线
                    },
                    {
                        "name": "BOLL下轨",
                        "type": "line",
                        "data": indicators['BOLL_lower'].round(2).tolist(),
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"width": 1, "opacity": 0.8, "color": "#14b143", "type": "dashed"}  # 下轨绿色
                    }
                ])
                legend_data.extend(["BOLL上轨", "BOLL中轨", "BOLL下轨"])
            
            # 更新图例
            echarts_option["legend"]["data"] = legend_data
            
            # 计算子图数量
            subplot_count = 1  # K线图
            if 'MACD' in requested_indicators:
                subplot_count += 1
            if 'KDJ' in requested_indicators:
                subplot_count += 1
            if 'RSI' in requested_indicators:
                subplot_count += 1
            if 'BIAS' in requested_indicators:
                subplot_count += 1
            
            # 如果有子图，需要调整布局 - 完全参考visualizer.py的布局逻辑
            if subplot_count > 1:
                # 参考visualizer.py：每个子图的高度为 f"{80/subplot_count}%"
                # K线图位置：pos_top="6%", height=f"{80/subplot_count}%"
                # 后续子图：current_top += 80/subplot_count + 5
                
                # 计算每个子图的高度百分比
                subplot_height = 80 / subplot_count
                
                # 调整K线图高度和位置 - 参考visualizer.py
                echarts_option["grid"][0]["height"] = f"{subplot_height}%"
                echarts_option["grid"][0]["top"] = "14%"  # 图例在6%结束，K线图从14%开始
                
                # 添加子图 - 从K线图下方开始
                current_top = 14 + subplot_height + 5  # 参考visualizer.py的计算方式
                
                # 添加MACD子图
                if 'MACD' in requested_indicators and 'MACD' in indicators:
                    macd_series = self._create_macd_series(dates, indicators)
                    echarts_option["series"].extend(macd_series)
                    
                    # 添加MACD系列到图例
                    legend_data.extend(["MACD", "Signal", "MACD柱"])
                    
                    # 添加MACD的Y轴
                    macd_yaxis = {
                        "scale": True,
                        "gridIndex": 1,
                        "splitNumber": 2,
                        "axisLabel": {"show": False},
                        "axisLine": {"show": False},
                        "axisTick": {"show": False},
                        "splitLine": {"show": False}
                    }
                    echarts_option["yAxis"].append(macd_yaxis)
                    
                    # 添加MACD的X轴
                    macd_xaxis = {
                        "type": "category",
                        "gridIndex": 1,
                        "data": dates,
                        "boundaryGap": True,
                        "axisLine": {"onZero": False},
                        "axisTick": {"show": False},
                        "splitLine": {"show": False},
                        "axisLabel": {"show": False},
                        "min": -0.2,
                        "max": len(dates) - 0.8
                    }
                    echarts_option["xAxis"].append(macd_xaxis)
                    
                    # 添加MACD网格 - 完全参考visualizer.py的布局
                    macd_grid = {
                        "left": "12%",
                        "right": "10%",
                        "top": f"{current_top}%",
                        "height": f"{subplot_height}%"  # 使用计算好的子图高度
                    }
                    echarts_option["grid"].append(macd_grid)
                    
                    current_top += subplot_height + 5  # 参考visualizer.py：增加5%的间距
                
                # 添加KDJ子图
                if 'KDJ' in requested_indicators and 'K' in indicators:
                    kdj_series = self._create_kdj_series(dates, indicators)
                    echarts_option["series"].extend(kdj_series)
                    
                    # 添加KDJ系列到图例
                    legend_data.extend(["K", "D", "J"])
                    
                    # 添加KDJ的Y轴
                    kdj_yaxis = {
                        "scale": True,
                        "gridIndex": 2,
                        "splitNumber": 2,
                        "axisLabel": {"show": False},
                        "axisLine": {"show": False},
                        "axisTick": {"show": False},
                        "splitLine": {"show": False},
                        "min": 0,
                        "max": 100
                    }
                    echarts_option["yAxis"].append(kdj_yaxis)
                    
                    # 添加KDJ的X轴
                    kdj_xaxis = {
                        "type": "category",
                        "gridIndex": 2,
                        "data": dates,
                        "boundaryGap": True,
                        "axisLine": {"onZero": False},
                        "axisTick": {"show": False},
                        "splitLine": {"show": False},
                        "axisLabel": {"show": False},
                        "min": -0.2,
                        "max": len(dates) - 0.8
                    }
                    echarts_option["xAxis"].append(kdj_xaxis)
                    
                    # 添加KDJ网格 - 完全参考visualizer.py的布局
                    kdj_grid = {
                        "left": "12%",
                        "right": "10%",
                        "top": f"{current_top}%",
                        "height": f"{subplot_height}%"  # 使用计算好的子图高度
                    }
                    echarts_option["grid"].append(kdj_grid)
                    
                    current_top += subplot_height + 5  # 参考visualizer.py：增加5%的间距
                
            # 更新图例
            echarts_option["legend"]["data"] = legend_data
            
            return echarts_option
            
        except Exception as e:
            logger.error(f"转换ECharts配置失败: {e}")
            raise
    
    def _get_stock_name(self, stock_code):
        """获取股票名称"""
        try:
            import akshare as ak
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                return stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0]
            else:
                return stock_code
        except:
            return stock_code
    
    def _get_frequency_display(self, frequency):
        """获取频率的中文显示"""
        frequency_map = {
            'daily': '日线',
            'weekly': '周线', 
            'monthly': '月线',
            '1min': '1分钟',
            '5min': '5分钟',
            '15min': '15分钟',
            '30min': '30分钟',
            '60min': '60分钟'
        }
        return frequency_map.get(frequency, '日线')
    
    def _create_macd_series(self, dates, indicators):
        """创建MACD系列"""
        series = []
        
        # MACD线
        series.append({
            "name": "MACD",
            "type": "line",
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "data": indicators['MACD'].round(4).tolist(),
            "smooth": True,
            "symbol": "none",
            "lineStyle": {"width": 1, "opacity": 0.8, "color": "#FF6B6B"}
        })
        
        # Signal线
        series.append({
            "name": "Signal",
            "type": "line",
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "data": indicators['MACD_signal'].round(4).tolist(),
            "smooth": True,
            "symbol": "none",
            "lineStyle": {"width": 1, "opacity": 0.8, "color": "#4ECDC4"}
        })
        
        # MACD柱状图 - 正值为红色，负值为绿色
        macd_hist_data = indicators['MACD_hist'].round(4).tolist()
        # 创建带颜色的数据
        macd_hist_colored = []
        for value in macd_hist_data:
            if value >= 0:
                color = "#ef232a"  # 正值为红色
            else:
                color = "#14b143"  # 负值为绿色
            
            macd_hist_colored.append({
                "value": value,
                "itemStyle": {
                    "color": color
                }
            })
        
        series.append({
            "name": "MACD柱",
            "type": "bar",
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "data": macd_hist_colored
        })
        
        return series
    
    def _create_kdj_series(self, dates, indicators):
        """创建KDJ系列"""
        series = []
        
        # K线
        series.append({
            "name": "K",
            "type": "line",
            "xAxisIndex": 2,
            "yAxisIndex": 2,
            "data": indicators['K'].round(2).tolist(),
            "smooth": True,
            "symbol": "none",
            "lineStyle": {"width": 1, "opacity": 0.8, "color": "#FF6B6B"},
            "connectNulls": True  # 连接空值
        })
        
        # D线
        series.append({
            "name": "D",
            "type": "line",
            "xAxisIndex": 2,
            "yAxisIndex": 2,
            "data": indicators['D'].round(2).tolist(),
            "smooth": True,
            "symbol": "none",
            "lineStyle": {"width": 1, "opacity": 0.8, "color": "#4ECDC4"},
            "connectNulls": True  # 连接空值
        })
        
        # J线
        series.append({
            "name": "J",
            "type": "line",
            "xAxisIndex": 2,
            "yAxisIndex": 2,
            "data": indicators['J'].round(2).tolist(),
            "smooth": True,
            "symbol": "none",
            "lineStyle": {"width": 1, "opacity": 0.8, "color": "#45B7D1"},
            "connectNulls": True  # 连接空值
        })
        
        return series
    
    
    
    def _save_svg_to_local(self, svg_content: str, stock_code: str = "", indicators: str = "") -> str:
        """
        保存SVG内容到本地文件
        """
        try:
            from datetime import datetime
            
            # 确保保存目录存在
            os.makedirs(self.save_path, exist_ok=True)
            
            # 生成文件名（包含股票代码、指标和时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 构建文件名前缀
            prefix_parts = []
            if stock_code:
                prefix_parts.append(stock_code)
            if indicators:
                # 清理指标名称，移除空格和特殊字符
                clean_indicators = indicators.replace(" ", "").replace(",", "_")
                prefix_parts.append(clean_indicators)
            
            if prefix_parts:
                prefix = "_".join(prefix_parts)
                filename = f"{prefix}_{timestamp}.svg"
            else:
                filename = f"chart_image_{timestamp}.svg"
                
            file_path = os.path.join(self.save_path, filename)
            
            # 保存SVG内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            logger.info(f"SVG文件已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存SVG文件失败: {e}")
            raise

    def _save_png_to_local(self, png_base64: str, stock_code: str = "", indicators: str = "") -> str:
        """
        保存PNG base64数据到本地文件
        """
        try:
            import base64
            from datetime import datetime
            
            # 确保保存目录存在
            os.makedirs(self.save_path, exist_ok=True)
            
            # 生成文件名（包含股票代码、指标和时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 构建文件名前缀
            prefix_parts = []
            if stock_code:
                prefix_parts.append(stock_code)
            if indicators:
                # 清理指标名称，移除空格和特殊字符
                clean_indicators = indicators.replace(" ", "").replace(",", "_")
                prefix_parts.append(clean_indicators)
            
            if prefix_parts:
                prefix = "_".join(prefix_parts)
                filename = f"{prefix}_{timestamp}.png"
            else:
                filename = f"chart_image_{timestamp}.png"
                
            file_path = os.path.join(self.save_path, filename)
            
            # 解码base64数据并保存
            image_bytes = base64.b64decode(png_base64)
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"PNG图片已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存PNG文件失败: {e}")
            raise

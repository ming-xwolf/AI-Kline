document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const analyzeForm = document.getElementById('analyzeForm');
    const stockCodeInput = document.getElementById('stockCode');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const chartsArea = document.getElementById('chartsArea');
    const chartImages = document.getElementById('chartImages');
    const analysisResult = document.getElementById('analysisResult');
    const analysisText = document.getElementById('analysisText');
    const stockInfoCard = document.getElementById('stockInfoCard');
    const stockInfoBody = document.getElementById('stockInfoBody');
    const chanAnalyzeBtn = document.getElementById('chanAnalyzeBtn');
    const chanAnalysisResult = document.getElementById('chanAnalysisResult');
    const chanAnalysisText = document.getElementById('chanAnalysisText');
    const chanChartArea = document.getElementById('chanChartArea');
    const chanChartImages = document.getElementById('chanChartImages');
    
    // 处理表单提交
    analyzeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const stockCode = stockCodeInput.value.trim();
        if (!stockCode) {
            alert('请输入股票代码');
            return;
        }
        
        // 显示加载指示器，隐藏结果区域
        loadingIndicator.classList.remove('d-none');
        chartsArea.classList.add('d-none');
        analysisResult.classList.add('d-none');
        
        // 获取股票基本信息
        fetchStockInfo(stockCode);
        
        // 发送分析请求
        const formData = new FormData(analyzeForm);
        axios.post('/analyze', formData)
            .then(response => {
                // 隐藏加载指示器
                loadingIndicator.classList.add('d-none');
                
                if (response.data.success) {
                    // 显示图表
                    displayCharts(response.data.charts, stockCode);
                    
                    // 显示分析结果
                    displayAnalysisResult(response.data.analysis_result);
                }
            })
            .catch(error => {
                loadingIndicator.classList.add('d-none');
                let errorMessage = '分析过程中出错';
                
                if (error.response && error.response.data && error.response.data.error) {
                    errorMessage = error.response.data.error;
                }
                
                alert(errorMessage);
                console.error('Error:', error);
            });
    });
    
    /**
     * 获取股票基本信息
     */
    function fetchStockInfo(stockCode) {
        stockInfoCard.classList.add('d-none');
        
        axios.get(`/stock_info/${stockCode}`)
            .then(response => {
                if (response.data.success) {
                    displayStockInfo(response.data.data);
                }
            })
            .catch(error => {
                console.error('Error fetching stock info:', error);
            });
    }
    
    /**
     * 显示股票基本信息
     */
    function displayStockInfo(data) {
        stockInfoBody.innerHTML = '';
        
        if (!data || Object.keys(data).length === 0) {
            stockInfoBody.innerHTML = '<p class="text-center text-muted">无法获取股票信息</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.className = 'table table-striped table-sm stock-info-table';
        
        const tbody = document.createElement('tbody');
        
        // 常用信息，优先显示
        const priorityFields = [
            '股票简称', '股票代码', '所处行业',
            '最新价', '涨跌幅', '成交量(万)', '成交额(万)',
            '总市值', '流通市值', '市盈率', '市净率'
        ];
        
        // 先显示优先信息
        for (const field of priorityFields) {
            if (data[field]) {
                const row = createInfoRow(field, data[field]);
                tbody.appendChild(row);
            }
        }
        
        // 再显示其他信息
        for (const [key, value] of Object.entries(data)) {
            if (!priorityFields.includes(key)) {
                const row = createInfoRow(key, value);
                tbody.appendChild(row);
            }
        }
        
        table.appendChild(tbody);
        stockInfoBody.appendChild(table);
        stockInfoCard.classList.remove('d-none');
    }
    
    /**
     * 创建信息行
     */
    function createInfoRow(label, value) {
        const row = document.createElement('tr');
        
        const th = document.createElement('th');
        th.textContent = label;
        
        const td = document.createElement('td');
        td.textContent = value;
        
        // 为涨跌幅添加颜色
        if (label === '涨跌幅') {
            if (value.includes('-')) {
                td.className = 'text-success';
            } else if (value.includes('+') || parseFloat(value) > 0) {
                td.className = 'text-danger';
            }
        }
        
        row.appendChild(th);
        row.appendChild(td);
        
        return row;
    }
    
    /**
     * 显示图表
     */
    function displayCharts(charts, stockCode) {
        chartImages.innerHTML = '';
        
        if (!charts || charts.length === 0) {
            chartImages.innerHTML = '<p class="text-center text-muted">未找到图表</p>';
            return;
        }
        
        // 只筛选出HTML交互式图表
        const htmlCharts = charts.filter(chart => chart.endsWith('.html'));
        
        if (htmlCharts.length === 0) {
            chartImages.innerHTML = '<p class="text-center text-muted">未找到交互式图表</p>';
            return;
        }
        
        // 添加图表
        for (const chart of htmlCharts) {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container';
            
            // 添加加载提示
            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'chart-loading';
            loadingMsg.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> <span>图表加载中...</span>';
            chartDiv.appendChild(loadingMsg);
            
            // HTML交互图表
            const iframe = document.createElement('iframe');
            iframe.src = `/output/charts/${chart}`;
            iframe.style.width = '100%';
            iframe.style.height = '700px'; // 增加高度与pyecharts图表设置一致
            iframe.style.border = 'none';
            iframe.onload = function() {
                // 图表加载完成后，隐藏加载提示
                loadingMsg.style.display = 'none';
            };
            chartDiv.appendChild(iframe);
            
            // 添加链接打开新窗口查看
            const link = document.createElement('a');
            link.href = `/output/charts/${chart}`;
            link.target = '_blank';
            link.className = 'btn btn-sm btn-outline-primary mt-2';
            link.textContent = '在新窗口中查看';
            chartDiv.appendChild(link);
            
            chartImages.appendChild(chartDiv);
        }
        
        chartsArea.classList.remove('d-none');
    }
    
    /**
     * 显示分析结果
     */
    function displayAnalysisResult(result) {
        if (!result) {
            analysisResult.classList.add('d-none');
            return;
        }
        
        // 将Markdown格式转换为HTML富文本
        const htmlResult = convertMarkdownToHTML(result);
        
        // 使用innerHTML以支持HTML标签
        analysisText.innerHTML = htmlResult;
        analysisResult.classList.remove('d-none');
    }
    
    /**
     * 将Markdown格式转换为HTML
     */
    function convertMarkdownToHTML(markdown) {
        if (!markdown) return '';
        
        // 替换标题 (# 标题)
        let html = markdown.replace(/^# (.+)$/gm, '<h1 class="mb-3">$1</h1>');
        html = html.replace(/^## (.+)$/gm, '<h2 class="mb-3 mt-4">$1</h2>');
        html = html.replace(/^### (.+)$/gm, '<h3 class="mb-2 mt-3">$1</h3>');
        html = html.replace(/^#### (.+)$/gm, '<h4 class="mb-2 mt-3">$1</h4>');
        
        // 替换粗体 (**文字**)
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // 替换斜体 (*文字*)
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // 替换超链接 [文本](链接)
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-decoration-none">$1</a>');
        
        // 替换引用 (> 文字)
        html = html.replace(/^> (.+)$/gm, '<blockquote class="blockquote ps-3 border-start border-4 border-primary text-muted">$1</blockquote>');
        
        // 处理表格
        const tableRegex = /^\|(.+)\|\s*\n\|([\s-:]+)\|\s*\n((^\|.+\|\s*\n)+)/gm;
        html = html.replace(tableRegex, function(match, header, separator, rows) {
            // 处理表头
            const headers = header.split('|').map(h => h.trim()).filter(h => h);
            const headerRow = '<tr>' + headers.map(h => `<th scope="col">${h}</th>`).join('') + '</tr>';
            
            // 处理行
            const tableRows = rows.split('\n').filter(row => row.trim());
            const bodyRows = tableRows.map(row => {
                const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
                return '<tr>' + cells.map(cell => `<td>${cell}</td>`).join('') + '</tr>';
            }).join('');
            
            return `<div class="table-responsive mb-3"><table class="table table-striped table-hover"><thead>${headerRow}</thead><tbody>${bodyRows}</tbody></table></div>`;
        });
        
        // 替换无序列表 (- 项目)
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>').replace(/<li>(.+)<\/li>\n<li>/g, '<li>$1</li>\n<li>');
        // 将连续的<li>元素包装在<ul>中
        let parts = html.split('\n');
        let inList = false;
        for (let i = 0; i < parts.length; i++) {
            if (parts[i].startsWith('<li>') && !inList) {
                parts[i] = '<ul class="mb-3">' + parts[i];
                inList = true;
            } else if (!parts[i].startsWith('<li>') && inList) {
                parts[i-1] = parts[i-1] + '</ul>';
                inList = false;
            }
        }
        if (inList) {
            parts[parts.length-1] = parts[parts.length-1] + '</ul>';
        }
        html = parts.join('\n');
        
        // 替换段落 (普通文本行)，但排除已经转换过的HTML
        html = html.replace(/^([^<\n].+)$/gm, '<p>$1</p>');
        
        // 处理空行
        html = html.replace(/\n\s*\n/g, '<br>');
        
        // 添加股票代码和股价的高亮显示
        html = html.replace(/\b(\d{6})\b/g, '<span class="badge bg-secondary">$1</span>');
        html = html.replace(/([^-])([\d.]+%)/g, '$1<span class="text-danger">$2</span>');
        html = html.replace(/(-[\d.]+%)/g, '<span class="text-success">$1</span>');
        
        // 为重要数据添加高亮
        html = html.replace(/([（(]?)((?:目标价|支撑位|压力位|止损位)[：:]([\d.]+)([）)]?))/g, 
            '$1<span class="stock-highlight">$2</span>');
            
        // 为重要提示添加醒目样式
        html = html.replace(/(注意|提示|风险|建议|总结|结论|策略)[:：]/g, 
            '<span class="text-danger fw-bold">$1：</span>');
        
        return html;
    }

    // 缠论分析按钮事件处理
    chanAnalyzeBtn.addEventListener('click', function() {
        const stockCode = stockCodeInput.value.trim();
        if (!stockCode) {
            alert('请先输入股票代码');
            return;
        }
        
        // 显示加载指示器，隐藏缠论分析结果区域
        loadingIndicator.classList.remove('d-none');
        chanAnalysisResult.classList.add('d-none');
        chanChartArea.classList.add('d-none');
        
        // 获取分析周期
        const period = document.getElementById('period').value;
        
        // 发送缠论分析请求
        const formData = new FormData();
        formData.append('stock_code', stockCode);
        formData.append('period', period);
        
        axios.post('/chan_analyze', formData)
            .then(response => {
                // 隐藏加载指示器
                loadingIndicator.classList.add('d-none');
                
                if (response.data.success) {
                    // 显示缠论分析结果
                    displayChanAnalysisResult(response.data.analysis_report, response.data.analysis_data);
                    
                    // 显示缠论分析图表
                    displayChanCharts(response.data.chart_path, stockCode);
                } else {
                    alert('缠论分析失败: ' + (response.data.error || '未知错误'));
                }
            })
            .catch(error => {
                loadingIndicator.classList.add('d-none');
                console.error('缠论分析错误:', error);
                alert('缠论分析过程中出错: ' + (error.response?.data?.error || error.message));
            });
    });
    
    // 显示缠论分析结果
    function displayChanAnalysisResult(analysisReport, analysisData) {
        chanAnalysisText.innerHTML = convertMarkdownToHTML(analysisReport);
        chanAnalysisResult.classList.remove('d-none');
        
        // 添加分析数据摘要
        if (analysisData) {
            const summaryHtml = `
                <div class="row mb-3">
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="card-title">笔数量</h6>
                                <h4 class="text-primary">${analysisData.pen_count || 0}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="card-title">线段数量</h6>
                                <h4 class="text-success">${analysisData.segment_count || 0}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="card-title">中枢数量</h6>
                                <h4 class="text-info">${analysisData.zhongshu_count || 0}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="card-title">综合评分</h6>
                                <h4 class="text-warning">${(analysisData.overall_score * 100).toFixed(1)}%</h4>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            chanAnalysisText.innerHTML = summaryHtml + chanAnalysisText.innerHTML;
        }
    }
    
    // 显示缠论分析图表
    function displayChanCharts(chartPath, stockCode) {
        if (chartPath) {
            const chartHtml = `
                <div class="text-center">
                    <h6 class="mb-3">缠论分析图表</h6>
                    <img src="/output/charts/${stockCode}_chan_analysis.png" 
                         class="img-fluid rounded shadow" 
                         alt="缠论分析图表"
                         style="max-width: 100%; height: auto;">
                    <p class="text-muted mt-2">点击图片可查看大图</p>
                </div>
            `;
            chanChartImages.innerHTML = chartHtml;
            chanChartArea.classList.remove('d-none');
        }
    }
}); 
from collections import defaultdict
import subprocess


class WorkHourTracker:
    def __init__(self):
        # 内部结构: {person: {date: total_hours}}
        self._data = defaultdict(lambda: defaultdict(float))
    
    def add_manual_record(self, person: str, date: str, hours: float | str):
        """
        手动添加一条记录（覆盖式或累加式？这里按【累加】，符合业务）
        """
        try:
            hours = float(hours)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid hours value: {hours}")
        
        self._data[person][date] += hours
        print(f"📝 手动添加: {person} - {date} += {hours}h → 当日累计: {self._data[person][date]:.1f}h")
    
    def add_auto_record(self, person: str, date: str, hours: str | float):
        """
        自动添加（通常来自工单处理），逻辑同上
        """
        return self.add_manual_record(person, date, hours)  # 复用逻辑
    
    def get_total_hours(self, person: str, date: str) -> float:
        """查询某人某日的累计工时"""
        return self._data[person][date]
    
    def is_over_limit(self, person: str, date: str, limit: float = 10.0) -> bool:
        """判断是否超限"""
        return self.get_total_hours(person, date) >= limit
    
    def reset(self):
        """清空所有记录"""
        self._data.clear()
        print("🗑️ 工时记录已清空")
    
    def __repr__(self):
        lines = ["📊 当前工时记录:"]
        for person, dates in self._d.items():
            for date, hours in dates.items():
                lines.append(f"  {person}: {date} → {hours:.1f}h")
        return "\n".join(lines) if len(lines) > 1 else "📊 无记录"

# 全局实例（可在模块中导出）
# hour_tracker = WorkHourTracker()

import subprocess

def compress_pdf(input_path, output_path):
    command = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook',  # /screen, /ebook, /prepress
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    subprocess.run(command)
FILE_PATH = '.\ASI.pdf'
compress_pdf(FILE_PATH, 'compressed_file.pdf')
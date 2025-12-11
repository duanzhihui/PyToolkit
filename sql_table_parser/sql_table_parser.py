#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL表名解析器
使用正则表达式从SQL代码中提取所有表名
支持多种SQL语句类型：SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER等
"""

import re
from typing import Set, List, Dict
from pathlib import Path


class SQLTableParser:
    """SQL表名解析器类"""
    
    def __init__(self):
        """初始化解析器，定义各种SQL语句的正则表达式模式"""
        
        # 表名模式：支持 table, schema.table, `table`, "table" 等格式
        self.table_pattern = r'(?:`[^`]+`|"[^"]+"|[\w]+\.[\w]+|[\w]+)'
        
        # 各种SQL语句的正则表达式模式
        self.patterns = {
            # SELECT ... FROM table
            'select_from': re.compile(
                r'\bFROM\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # JOIN table
            'join': re.compile(
                r'\b(?:INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|CROSS\s+JOIN|JOIN)\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # INSERT INTO table
            'insert': re.compile(
                r'\bINSERT\s+INTO\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # UPDATE table
            'update': re.compile(
                r'\bUPDATE\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # DELETE FROM table
            'delete': re.compile(
                r'\bDELETE\s+FROM\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # CREATE TABLE table
            'create': re.compile(
                r'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # DROP TABLE table
            'drop': re.compile(
                r'\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # ALTER TABLE table
            'alter': re.compile(
                r'\bALTER\s+TABLE\s+' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # TRUNCATE TABLE table
            'truncate': re.compile(
                r'\bTRUNCATE\s+(?:TABLE\s+)?' + self.table_pattern,
                re.IGNORECASE
            ),
            
            # WITH cte_name AS (...)
            'cte': re.compile(
                r'\bWITH\s+(\w+)\s+AS',
                re.IGNORECASE
            ),
        }
        
        # SQL关键字集合，用于过滤非表名
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 
            'CROSS', 'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'AS', 'WITH',
            'UNION', 'INTERSECT', 'EXCEPT', 'ORDER', 'BY', 'GROUP', 'HAVING',
            'LIMIT', 'OFFSET', 'DISTINCT', 'ALL', 'ANY', 'SOME', 'CASE', 'WHEN',
            'THEN', 'ELSE', 'END', 'IF', 'NULL', 'IS', 'TRUE', 'FALSE', 'TRUNCATE',
            'ASC', 'DESC', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'CONSTRAINT',
            'UNIQUE', 'CHECK', 'DEFAULT', 'AUTO_INCREMENT', 'CASCADE'
        }
    
    def clean_table_name(self, table_name: str) -> str:
        """
        清理表名，去除引号、反引号等
        
        Args:
            table_name: 原始表名
            
        Returns:
            清理后的表名
        """
        # 去除前后空格
        table_name = table_name.strip()
        
        # 去除反引号和双引号
        table_name = table_name.strip('`"')
        
        return table_name
    
    def is_valid_table_name(self, table_name: str) -> bool:
        """
        验证是否为有效的表名
        
        Args:
            table_name: 表名
            
        Returns:
            是否有效
        """
        if not table_name:
            return False
        
        # 清理表名
        clean_name = self.clean_table_name(table_name)
        
        # 如果是schema.table格式，只检查table部分
        if '.' in clean_name:
            parts = clean_name.split('.')
            clean_name = parts[-1].strip('`"')
        
        # 检查是否为SQL关键字
        if clean_name.upper() in self.sql_keywords:
            return False
        
        # 检查是否为有效的标识符（字母、数字、下划线）
        if not re.match(r'^[a-zA-Z_]\w*$', clean_name):
            return False
        
        return True
    
    def remove_comments(self, sql: str) -> str:
        """
        移除SQL中的注释
        
        Args:
            sql: SQL代码
            
        Returns:
            移除注释后的SQL
        """
        # 移除单行注释 --
        sql = re.sub(r'--[^\n]*', '', sql)
        
        # 移除多行注释 /* */
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        return sql
    
    def extract_tables_from_pattern(self, sql: str, pattern: re.Pattern) -> Set[str]:
        """
        使用指定的正则表达式模式提取表名
        
        Args:
            sql: SQL代码
            pattern: 正则表达式模式
            
        Returns:
            表名集合
        """
        tables = set()
        matches = pattern.finditer(sql)
        
        for match in matches:
            # 获取匹配的完整文本
            matched_text = match.group(0)
            
            # 提取表名部分（去除关键字）
            # 分割匹配文本，取最后一个非空白部分
            parts = matched_text.split()
            if parts:
                table_name = parts[-1]
                
                # 清理并验证表名
                clean_name = self.clean_table_name(table_name)
                if self.is_valid_table_name(clean_name):
                    tables.add(clean_name)
        
        return tables
    
    def parse_sql(self, sql: str) -> Dict[str, Set[str]]:
        """
        解析SQL代码，提取所有表名
        
        Args:
            sql: SQL代码
            
        Returns:
            字典，键为SQL语句类型，值为表名集合
        """
        # 移除注释
        sql = self.remove_comments(sql)
        
        result = {}
        all_tables = set()
        
        # 使用各种模式提取表名
        for pattern_name, pattern in self.patterns.items():
            tables = self.extract_tables_from_pattern(sql, pattern)
            if tables:
                result[pattern_name] = tables
                all_tables.update(tables)
        
        # 添加所有表名的汇总
        result['all_tables'] = all_tables
        
        return result
    
    def parse_file(self, file_path: str) -> Dict[str, Set[str]]:
        """
        解析SQL文件
        
        Args:
            file_path: SQL文件路径
            
        Returns:
            字典，键为SQL语句类型，值为表名集合
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        return self.parse_sql(sql)
    
    def format_result(self, result: Dict[str, Set[str]]) -> str:
        """
        格式化解析结果为可读字符串
        
        Args:
            result: 解析结果
            
        Returns:
            格式化后的字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("SQL表名解析结果")
        lines.append("=" * 60)
        
        # 显示所有表名
        if 'all_tables' in result:
            lines.append(f"\n【所有表名】 (共 {len(result['all_tables'])} 个)")
            for table in sorted(result['all_tables']):
                lines.append(f"  - {table}")
        
        # 按语句类型显示
        lines.append("\n【按SQL语句类型分类】")
        
        type_names = {
            'select_from': 'SELECT FROM',
            'join': 'JOIN',
            'insert': 'INSERT INTO',
            'update': 'UPDATE',
            'delete': 'DELETE FROM',
            'create': 'CREATE TABLE',
            'drop': 'DROP TABLE',
            'alter': 'ALTER TABLE',
            'truncate': 'TRUNCATE TABLE',
            'cte': 'WITH (CTE)',
        }
        
        for pattern_name, tables in result.items():
            if pattern_name != 'all_tables' and tables:
                type_name = type_names.get(pattern_name, pattern_name)
                lines.append(f"\n{type_name}: {len(tables)} 个表")
                for table in sorted(tables):
                    lines.append(f"  - {table}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)


def main():
    """主函数，演示如何使用SQL表名解析器"""
    
    # 创建解析器实例
    parser = SQLTableParser()
    
    # 示例1：解析SQL字符串
    print("示例1：解析SQL字符串")
    print("-" * 60)
    
    sample_sql = """
    SELECT u.id, u.name, o.order_id
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'active';
    
    INSERT INTO logs (message, created_at) VALUES ('test', NOW());
    
    UPDATE products SET price = price * 1.1 WHERE category = 'electronics';
    """
    
    result = parser.parse_sql(sample_sql)
    print(parser.format_result(result))
    
    # 示例2：解析SQL文件
    print("\n\n示例2：解析SQL文件")
    print("-" * 60)
    
    sql_file = "sample_queries.sql"
    
    try:
        result = parser.parse_file(sql_file)
        print(parser.format_result(result))
        
        # 保存结果到文件
        output_file = "parse_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(parser.format_result(result))
        print(f"\n解析结果已保存到: {output_file}")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print(f"请确保 {sql_file} 文件存在于当前目录")


if __name__ == "__main__":
    main()

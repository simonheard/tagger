# locales.py
# 所有 UI 文本集中管理，支持中英文

LOCALES = {
    'en': {
        'app_title': 'File & Folder Tagger',
        'select_folder': 'Select Folder',
        'select_files': 'Select Files',
        'refresh': 'Refresh',
        'custom_tag_placeholder': 'Custom Tag',
        'add_custom_tag': 'Add Custom Tag',
        'tag_filter': 'Tag Filter:',
        'type_filter': 'Type Filter:',
        'all': 'All',
        'select_all': 'Select All',
        'remove_tags': 'Remove Tags',
        'usage_button': 'Usage',
        'usage_text': """
Usage

1. Select Folder: scan entire folder (including subdirs).
2. Select Files: pick multiple files for batch operations.
3. Add Tag: click an existing tag button or enter in “Custom Tag” then click “Add Custom Tag”.
4. Remove Tags: select items then click “Remove Tags”.
5. Filter: use “Tag Filter” + “Type Filter” to narrow list.
6. Select All: click “Select All” or press Ctrl+A.
7. Refresh: click “Refresh” after external renames/additions to update list.

Tag Rules
- Always start with #, lowercase, words joined by _.
- Max length 120 chars, too-long tags skipped.
- File example: name_[#tag1,#tag2].ext
- Folders have no extension; same rules apply.
""",
        'error_rename_fail_title': 'Rename Error',
        'error_rename_fail_msg': 'Cannot find: {path}',
        'warning_long_tag_title': 'Tag Too Long',
        'warning_long_tag_msg': 'Tag "{tag}" exceeds {max} chars and was skipped',
        'close': 'Close',
        'folder': 'folder',
    },
    'zh': {
        'app_title': '文件/文件夹 标签工具',
        'select_folder': '选择文件夹',
        'select_files': '选择文件',
        'refresh': '刷新',
        'custom_tag_placeholder': '自定义标签',
        'add_custom_tag': '添加自定义标签',
        'tag_filter': '标签过滤：',
        'type_filter': '类型过滤：',
        'all': '全部',
        'select_all': '全选',
        'remove_tags': '移除标签',
        'usage_button': '使用说明',
        'usage_text': """
使用说明

1. 选择文件夹：扫描整个文件夹（包括子目录）。
2. 选择文件：直接选中多个文件进行批量操作。
3. 添加标签：点击已有标签按钮，或在“自定义标签”输入后点击“添加自定义标签”。
4. 移除标签：选中列表项后，点击“移除标签”。
5. 过滤列表：可组合“标签过滤”与“类型过滤”进行筛选。
6. 全选：点击“全选”或使用 Ctrl+A 快捷键。
7. 刷新：当外部重命名或新增文件时，点击“刷新”更新列表。

标签规则
- 必须以 # 开头，全部小写，单词间用下划线分隔。
- 最长不超过 120 字符，超长自动跳过。
- 文件示例：name_[#tag1,#tag2].ext
- 文件夹无扩展名，重命名时同样规则。
""",
        'error_rename_fail_title': '重命名失败',
        'error_rename_fail_msg': '找不到：{path}',
        'warning_long_tag_title': '标签太长',
        'warning_long_tag_msg': '标签 "{tag}" 超过 {max} 字符，已跳过',
        'close': '关闭',
        'folder': '文件夹',
    }
}

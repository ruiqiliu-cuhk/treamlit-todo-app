import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 确保数据目录存在
if not os.path.exists('data'):
    os.makedirs('data')

# 数据文件路径
DATA_FILE = 'data/todos.csv'

# 初始化或加载待办事项数据
def load_todos():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # 确保必要的列存在
            if not all(col in df.columns for col in ['task', 'completed', 'created_at', 'completed_at']):
                df = pd.DataFrame(columns=['task', 'completed', 'created_at', 'completed_at'])
        except Exception as e:
            st.error(f"加载数据时出错: {e}")
            df = pd.DataFrame(columns=['task', 'completed', 'created_at', 'completed_at'])
    else:
        df = pd.DataFrame(columns=['task', 'completed', 'created_at', 'completed_at'])
    return df

def save_todos(df):
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"保存数据时出错: {e}")

def main():
    st.title("📝 待办事项管理")
    st.markdown("使用这个应用来管理你的日常任务。")
    
    # 加载待办事项
    todos_df = load_todos()
    
    # 侧边栏 - 统计信息
    st.sidebar.header("📊 统计信息")
    total_todos = len(todos_df)
    completed_todos = len(todos_df[todos_df['completed'] == True])
    pending_todos = total_todos - completed_todos
    
    st.sidebar.metric("总待办事项", total_todos)
    st.sidebar.metric("已完成", completed_todos)
    st.sidebar.metric("未完成", pending_todos)
    
    if pending_todos > 0:
        progress = completed_todos / total_todos * 100
        st.sidebar.progress(progress / 100)
        st.sidebar.write(f"完成进度: {progress:.1f}%")
    
    # 主界面 - 添加新待办事项
    st.header("添加新待办事项")
    new_task = st.text_input("输入新任务", "")
    if st.button("添加任务"):
        if new_task:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_todo = pd.DataFrame({
                'task': [new_task],
                'completed': [False],
                'created_at': [now],
                'completed_at': [None]
            })
            todos_df = pd.concat([todos_df, new_todo], ignore_index=True)
            save_todos(todos_df)
            st.success(f"已添加任务: {new_task}")
            st.experimental_rerun()  # 刷新页面
        else:
            st.warning("任务内容不能为空!")
    
    # 主界面 - 显示待办事项
    st.header("待办事项列表")
    
    # 筛选选项
    filter_option = st.selectbox("筛选:", ["全部", "已完成", "未完成"])
    
    if filter_option == "已完成":
        filtered_todos = todos_df[todos_df['completed'] == True]
    elif filter_option == "未完成":
        filtered_todos = todos_df[todos_df['completed'] == False]
    else:
        filtered_todos = todos_df
    
    if not filtered_todos.empty:
        # 显示待办事项表格
        for index, row in filtered_todos.iterrows():
            col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
            
            # 任务状态和内容
            if row['completed']:
                task_text = f"~~{row['task']}~~"
                task_status = "✅"
            else:
                task_text = row['task']
                task_status = "🔲"
            
            col1.markdown(f"{task_status} {task_text}")
            col1.caption(f"创建于: {row['created_at']}")
            
            # 完成/未完成按钮
            if not row['completed']:
                if col2.button("完成", key=f"complete_{index}"):
                    todos_df.loc[index, 'completed'] = True
                    todos_df.loc[index, 'completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_todos(todos_df)
                    st.success(f"已标记任务为完成: {row['task']}")
                    st.experimental_rerun()
            else:
                if col2.button("恢复", key=f"uncomplete_{index}"):
                    todos_df.loc[index, 'completed'] = False
                    todos_df.loc[index, 'completed_at'] = None
                    save_todos(todos_df)
                    st.success(f"已恢复任务: {row['task']}")
                    st.experimental_rerun()
            
            # 编辑按钮
            if col3.button("编辑", key=f"edit_{index}"):
                edited_task = st.text_input("编辑任务", row['task'], key=f"edit_input_{index}")
                if st.button("保存编辑", key=f"save_edit_{index}"):
                    if edited_task:
                        todos_df.loc[index, 'task'] = edited_task
                        save_todos(todos_df)
                        st.success(f"已更新任务: {edited_task}")
                        st.experimental_rerun()
                    else:
                        st.warning("任务内容不能为空!")
            
            # 删除按钮
            if col4.button("删除", key=f"delete_{index}"):
                if st.confirm(f"确定要删除任务 '{row['task']}' 吗?"):
                    todos_df = todos_df.drop(index)
                    todos_df = todos_df.reset_index(drop=True)
                    save_todos(todos_df)
                    st.success(f"已删除任务: {row['task']}")
                    st.experimental_rerun()
    else:
        st.info("🎉 没有待办事项! 添加一个新任务开始吧.")
    
    # 批量操作
    st.header("批量操作")
    col1, col2 = st.columns(2)
    
    if col1.button("标记所有为完成"):
        if not todos_df.empty and any(~todos_df['completed']):
            if st.confirm("确定要将所有未完成的任务标记为完成吗?"):
                todos_df.loc[~todos_df['completed'], 'completed'] = True
                todos_df.loc[~todos_df['completed'], 'completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_todos(todos_df)
                st.success("已将所有任务标记为完成!")
                st.experimental_rerun()
        else:
            st.info("没有未完成的任务需要标记.")
    
    if col2.button("删除所有已完成"):
        if not todos_df.empty and any(todos_df['completed']):
            if st.confirm("确定要删除所有已完成的任务吗?"):
                todos_df = todos_df[~todos_df['completed']]
                todos_df = todos_df.reset_index(drop=True)
                save_todos(todos_df)
                st.success("已删除所有已完成的任务!")
                st.experimental_rerun()
        else:
            st.info("没有已完成的任务需要删除.")

if __name__ == "__main__":
    main()    
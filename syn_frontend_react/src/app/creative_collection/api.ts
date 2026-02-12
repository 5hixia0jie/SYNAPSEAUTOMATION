/**
 * 创意采集API调用函数
 */

import { CreativeCollection } from './types'

// API基础URL
const API_BASE_URL = '/api/v1'

// 采集请求参数
interface CollectRequest {
  video_url: string
}

// 采集响应
interface CollectResponse {
  task_id: string
}

// 任务状态响应
interface TaskStatusResponse {
  status: string
  progress: number
  data?: CreativeCollection
}

// 列表响应
interface ListResponse {
  items: CreativeCollection[]
  total: number
}

/**
 * 提交采集任务
 * @param videoUrl 视频链接
 * @returns 任务ID
 */
export async function submitCollectTask(videoUrl: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/creative_collection/collect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_url: videoUrl }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `提交失败: ${response.status}`)
    }

    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '提交失败')
    }

    return data.data.task_id
  } catch (error) {
    console.error('提交采集任务失败:', error)
    throw error
  }
}

/**
 * 获取采集任务状态
 * @param taskId 任务ID
 * @returns 任务状态
 */
export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/creative_collection/status/${taskId}`)

    if (!response.ok) {
      throw new Error(`获取任务状态失败: ${response.status}`)
    }

    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '获取任务状态失败')
    }

    return data.data
  } catch (error) {
    console.error('获取任务状态失败:', error)
    throw error
  }
}

/**
 * 获取采集列表
 * @param page 页码
 * @param pageSize 每页大小
 * @param status 状态筛选
 * @param platform 平台筛选
 * @returns 采集列表和总数
 */
export async function getCollectionList(
  page: number = 1,
  pageSize: number = 10,
  status?: string,
  platform?: string
): Promise<{ items: CreativeCollection[]; total: number }> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })

    if (status) {
      params.append('status', status)
    }

    if (platform) {
      params.append('platform', platform)
    }

    const response = await fetch(`${API_BASE_URL}/creative_collection/list?${params.toString()}`)

    if (!response.ok) {
      throw new Error(`获取采集列表失败: ${response.status}`)
    }

    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '获取采集列表失败')
    }

    return data.data
  } catch (error) {
    console.error('获取采集列表失败:', error)
    throw error
  }
}

/**
 * 获取采集详情
 * @param id 采集ID
 * @returns 采集详情
 */
export async function getCollectionDetail(id: number): Promise<CreativeCollection> {
  try {
    const response = await fetch(`${API_BASE_URL}/creative_collection/${id}`)

    if (!response.ok) {
      throw new Error(`获取采集详情失败: ${response.status}`)
    }

    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '获取采集详情失败')
    }

    return data.data
  } catch (error) {
    console.error('获取采集详情失败:', error)
    throw error
  }
}

/**
 * 删除采集项目
 * @param id 采集ID
 */
export async function deleteCollection(id: number): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/creative_collection/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`删除采集项目失败: ${response.status}`)
    }

    const data = await response.json()
    if (!data.success) {
      throw new Error(data.message || '删除采集项目失败')
    }
  } catch (error) {
    console.error('删除采集项目失败:', error)
    throw error
  }
}

/**
 * 创意采集类型定义
 */

/**
 * 创意采集项目类型
 */
export interface CreativeCollection {
  /** ID */
  id: number
  /** 标题 */
  title: string
  /** 标签 */
  tags: string[]
  /** 封面URL */
  cover_url: string
  /** 视频URL */
  video_url: string
  /** 拍摄脚本 */
  script: string
  /** 来源平台 */
  source_platform: string
  /** 状态 */
  status: 'success' | 'failed'
  /** 错误信息 */
  error_message?: string
  /** 创建时间 */
  created_at: string
  /** 更新时间 */
  updated_at: string
}

/**
 * 任务状态类型
 */
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'not_found'

/**
 * 平台类型
 */
export type PlatformType = '抖音' | '头条' | '未知'

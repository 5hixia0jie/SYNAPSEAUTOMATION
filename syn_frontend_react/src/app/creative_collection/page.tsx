"use client"

import * as React from "react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import { Plus, Search, Filter, Download, Trash2, Eye, Play, Link as LinkIcon, RefreshCw } from "lucide-react"

// 导入类型和API
import { CreativeCollection } from "./types"
import { submitCollectTask, getTaskStatus, getCollectionList, deleteCollection } from "./api"


function CreativeCollectionPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [collections, setCollections] = useState<CreativeCollection[]>([])
  const [total, setTotal] = useState(0)
  const [videoUrl, setVideoUrl] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<string>("")
  const [taskProgress, setTaskProgress] = useState(0)
  const [isTaskProcessing, setIsTaskProcessing] = useState(false)
  const [activeTab, setActiveTab] = useState("all")
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  // 删除确认对话框状态
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [currentDeleteId, setCurrentDeleteId] = useState<number | null>(null)

  // 获取采集列表
  const fetchCollections = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const status = activeTab === "all" ? undefined : activeTab
      const result = await getCollectionList(page, pageSize, status)
      setCollections(result.items)
      setTotal(result.total)
    } catch (err) {
      setError("获取数据失败，请重试")
      console.error("获取采集列表失败:", err)
    } finally {
      setIsLoading(false)
    }
  }

  // 初始加载数据
  useEffect(() => {
    fetchCollections()
  }, [page, pageSize, activeTab])

  // 轮询任务状态
  useEffect(() => {
    let interval: NodeJS.Timeout
    
    if (currentTaskId && isTaskProcessing) {
      interval = setInterval(async () => {
        try {
          const status = await getTaskStatus(currentTaskId)
          setTaskStatus(status.status)
          setTaskProgress(status.progress)
          
          if (status.status === "completed" || status.status === "failed") {
            clearInterval(interval)
            setIsTaskProcessing(false)
            
            // 如果任务成功，刷新列表
            if (status.status === "completed") {
              fetchCollections()
            }
          }
        } catch (err) {
          console.error("获取任务状态失败:", err)
          clearInterval(interval)
          setIsTaskProcessing(false)
        }
      }, 2000)
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [currentTaskId, isTaskProcessing])

  // 从输入文本中提取视频链接
  const extractVideoUrl = (input: string): string => {
    // 正则表达式匹配 URL
    const urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/g
    
    // 尝试匹配 URL
    const matches = input.match(urlRegex)
    if (matches && matches.length > 0) {
      // 返回第一个匹配的 URL
      return matches[0]
    }
    
    // 如果没有匹配到 URL，返回原始输入
    return input
  }

  // 提交采集请求
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!videoUrl) {
      setError("请输入视频链接")
      return
    }

    // 提取视频链接
    const extractedUrl = extractVideoUrl(videoUrl)
    console.log("提取的视频链接:", extractedUrl)

    setIsSubmitting(true)
    setError(null)

    try {
      // 调用API提交采集请求
      const taskId = await submitCollectTask(extractedUrl)
      setCurrentTaskId(taskId)
      setTaskStatus("pending")
      setTaskProgress(0)
      setIsTaskProcessing(true)
      setIsDialogOpen(false)
      setVideoUrl("")
    } catch (err) {
      setError("提交失败，请重试")
      console.error("提交采集任务失败:", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  // 处理删除
  const handleDelete = (id: number) => {
    setCurrentDeleteId(id)
    setIsDeleteDialogOpen(true)
  }

  // 确认删除
  const confirmDelete = async () => {
    if (!currentDeleteId) return

    try {
      await deleteCollection(currentDeleteId)
      // 刷新列表
      fetchCollections()
      // 关闭对话框
      setIsDeleteDialogOpen(false)
      setCurrentDeleteId(null)
    } catch (err) {
      setError("删除失败，请重试")
      console.error("删除采集项目失败:", err)
      // 关闭对话框
      setIsDeleteDialogOpen(false)
      setCurrentDeleteId(null)
    }
  }

  // 取消删除
  const cancelDelete = () => {
    setIsDeleteDialogOpen(false)
    setCurrentDeleteId(null)
  }

  // 格式化日期
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  // 处理标签切换
  const handleTabChange = (value: string) => {
    setActiveTab(value)
    setPage(1)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 页面标题和操作区 */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">创意采集</h1>
          <p className="text-gray-400 mt-1">从头条和抖音采集视频创意信息</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="mr-2 h-4 w-4" />
              手动采集
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-gray-900 border-gray-800 text-white">
            <DialogHeader>
              <DialogTitle>手动采集视频</DialogTitle>
              <DialogDescription className="text-gray-400">
                请输入来自头条或抖音的视频链接，系统将自动采集相关信息
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 py-4">
              {error && (
                <Alert variant="destructive" className="bg-red-900/30 border-red-800">
                  <AlertTitle>错误</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="space-y-2">
                <Label htmlFor="video-url" className="text-white">视频链接</Label>
                <Input
                  id="video-url"
                  placeholder="https://www.douyin.com/video/1234567890"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  disabled={isSubmitting}
                  className="bg-gray-800 border-gray-700 text-white placeholder:text-gray-500"
                />
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setIsDialogOpen(false)
                    setVideoUrl("")
                    setError(null)
                  }}
                  disabled={isSubmitting}
                  className="bg-gray-700 hover:bg-gray-600 text-white"
                >
                  取消
                </Button>
                <Button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "提交中..." : "提交"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* 任务状态显示 */}
      {isTaskProcessing && currentTaskId && (
        <Alert className="mb-6 bg-blue-900/30 border-blue-800">
          <AlertTitle>采集任务处理中</AlertTitle>
          <AlertDescription className="mb-2">
            任务ID: {currentTaskId}
          </AlertDescription>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>状态: {taskStatus}</span>
              <span>进度: {taskProgress}%</span>
            </div>
            <Progress value={taskProgress} className="h-2 bg-blue-800/50">
              {taskProgress}%
            </Progress>
          </div>
        </Alert>
      )}

      {/* 筛选和搜索区 */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="搜索标题或标签"
            className="pl-8 bg-gray-800 border-gray-700 text-white placeholder:text-gray-500"
          />
        </div>
        <Button variant="secondary" className="bg-gray-700 hover:bg-gray-600 text-white">
          <Filter className="mr-2 h-4 w-4" />
          筛选
        </Button>
        <Button variant="secondary" className="bg-gray-700 hover:bg-gray-600 text-white">
          <Download className="mr-2 h-4 w-4" />
          导出
        </Button>
        <Button 
          variant="secondary" 
          className="bg-gray-700 hover:bg-gray-600 text-white"
          onClick={fetchCollections}
          disabled={isLoading}
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          刷新
        </Button>
      </div>

      {/* 标签页 */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="mb-6">
        <TabsList className="bg-gray-800">
          <TabsTrigger value="all" className="text-white data-[state=active]:bg-gray-700">
            全部
          </TabsTrigger>
          <TabsTrigger value="success" className="text-white data-[state=active]:bg-gray-700">
            成功
          </TabsTrigger>
          <TabsTrigger value="failed" className="text-white data-[state=active]:bg-gray-700">
            失败
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* 数据展示区 */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <Card key={index} className="bg-gray-800 border-gray-700">
              <CardHeader>
                <div className="h-4 w-3/4 mb-2 bg-gray-700 rounded"></div>
                <div className="h-3 w-1/2 bg-gray-700 rounded"></div>
              </CardHeader>
              <CardContent>
                <div className="h-48 w-full mb-4 bg-gray-700 rounded"></div>
                <div className="h-3 w-full mb-2 bg-gray-700 rounded"></div>
                <div className="h-3 w-2/3 bg-gray-700 rounded"></div>
              </CardContent>
              <CardFooter>
                <div className="h-8 w-20 mr-2 bg-gray-700 rounded"></div>
                <div className="h-8 w-20 bg-gray-700 rounded"></div>
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : collections.length === 0 ? (
        <Alert className="bg-gray-800 border-gray-700">
          <AlertTitle>暂无数据</AlertTitle>
          <AlertDescription>
            请点击"手动采集"按钮开始采集视频创意
          </AlertDescription>
        </Alert>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((item) => (
            <Card key={item.id} className="bg-gray-800 border-gray-700 overflow-hidden">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg font-semibold text-white line-clamp-2">
                    {item.title}
                  </CardTitle>
                  <Badge 
                    variant={item.status === "success" ? "default" : "destructive"} 
                    className={item.status === "success" ? "bg-green-900/50 text-green-400" : "bg-red-900/50 text-red-400"}
                  >
                    {item.status === "success" ? "成功" : "失败"}
                  </Badge>
                </div>
                <CardDescription className="text-gray-400">
                  {item.source_platform} · {formatDate(item.created_at)}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-2">
                <div className="relative h-48 w-full mb-4 overflow-hidden rounded-md">
                  <img 
                    src={item.cover_url} 
                    alt={item.title} 
                    className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://neeko-copilot.bytedance.net/api/text2image?prompt=video%20cover%20placeholder&size=800x600"
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end">
                    <div className="p-3">
                      <div className="flex flex-wrap gap-1">
                        {item.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="bg-gray-700 text-gray-300">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mb-4">
                  <Label className="text-sm font-medium text-gray-400 mb-1 block">
                    原视频链接
                  </Label>
                  <div className="flex items-center space-x-2">
                    <LinkIcon className="h-4 w-4 text-blue-400" />
                    <a 
                      href={item.video_url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-sm text-blue-400 hover:underline truncate"
                    >
                      {item.video_url}
                    </a>
                  </div>
                </div>
                {item.error_message && (
                  <div className="mt-2">
                    <Alert variant="destructive" className="bg-red-900/30 border-red-800">
                      <AlertDescription className="text-xs">
                        错误: {item.error_message}
                      </AlertDescription>
                    </Alert>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-between pt-2">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  className="bg-gray-700 hover:bg-gray-600 text-white"
                  onClick={() => {
                    // 查看详情
                    console.log("查看详情:", item.id)
                  }}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  查看
                </Button>
                <Button 
                  variant="destructive" 
                  size="sm" 
                  className="bg-red-900/50 hover:bg-red-900 text-red-400"
                  onClick={() => handleDelete(item.id)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  删除
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* 分页区 */}
      {!isLoading && collections.length > 0 && (
        <div className="mt-8 flex justify-between items-center">
          <div className="text-gray-400 text-sm">
            共 {total} 条记录
          </div>
          <div className="flex space-x-2">
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={page === 1} 
              className="bg-gray-700 hover:bg-gray-600 text-white"
              onClick={() => setPage(page - 1)}
            >
              上一页
            </Button>
            <Button variant="secondary" size="sm" className="bg-gray-700 hover:bg-gray-600 text-white">
              {page}
            </Button>
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={page * pageSize >= total} 
              className="bg-gray-700 hover:bg-gray-600 text-white"
              onClick={() => setPage(page + 1)}
            >
              下一页
            </Button>
          </div>
        </div>
      )}

      {/* 删除确认对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white">
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription className="text-gray-400">
              确定要删除这个采集项目吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={cancelDelete}
              className="bg-gray-700 hover:bg-gray-600 text-white"
            >
              取消
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={confirmDelete}
              className="bg-red-900/50 hover:bg-red-900 text-red-400"
            >
              确认删除
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default CreativeCollectionPage

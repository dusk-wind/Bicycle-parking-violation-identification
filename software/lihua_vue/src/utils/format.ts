/**
 * 格式化置信度显示
 * @param confidence 置信度值
 * @returns 格式化后的置信度字符串
 */
export const formatConfidence = (confidence: number): string => {
  if (confidence == null || confidence === undefined) {
    return '0.0';
  }
  
  // 如果置信度是小数形式(0-1)，转换为百分比
  if (confidence <= 1) {
    return (confidence * 100).toFixed(1);
  }
  
  // 如果置信度已经是百分比形式(0-100)，保持原样
  return confidence.toFixed(1);
};

/**
 * 获取置信度等级
 * @param confidence 置信度值
 * @returns 置信度等级 'high' | 'medium' | 'low'
 */
export const getConfidenceLevel = (confidence: number): 'high' | 'medium' | 'low' => {
  if (confidence == null || confidence === undefined) {
    return 'low';
  }
  
  const confNum = confidence <= 1 ? confidence * 100 : confidence;
  if (confNum > 70) return 'high';
  if (confNum >= 50) return 'medium';
  return 'low';
}; 
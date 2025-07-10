package com.lihua.demo.Camera.mapper;

import com.lihua.demo.Camera.entity.Camera;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 摄像头Mapper接口
 * @author lihua
 */
@Mapper
public interface CameraMapper {
    
    /**
     * 查询所有摄像头
     * @return 摄像头列表
     */
    List<Camera> selectAll();
    
    /**
     * 根据ID查询摄像头
     * @param id 摄像头ID
     * @return 摄像头信息
     */
    Camera selectById(@Param("id") Long id);
    
    /**
     * 统计总摄像头数
     * @return 总数
     */
    Long countTotal();
    
    /**
     * 按连接状态统计摄像头数
     * @param connected 连接状态
     * @return 数量
     */
    Long countByConnected(@Param("connected") Boolean connected);
    
    /**
     * 更新摄像头连接状态
     * @param id 摄像头ID
     * @param connected 连接状态
     * @return 影响行数
     */
    int updateConnectedStatus(@Param("id") Long id, @Param("connected") Boolean connected);
    
    /**
     * 插入摄像头
     * @param camera 摄像头信息
     * @return 影响行数
     */
    int insert(Camera camera);
    
    /**
     * 更新摄像头信息
     * @param camera 摄像头信息
     * @return 影响行数
     */
    int update(Camera camera);
    
    /**
     * 删除摄像头
     * @param id 摄像头ID
     * @return 影响行数
     */
    int deleteById(@Param("id") Long id);
} 
package com.lihua.handle;

import com.lihua.enums.ResultCodeEnum;
import com.lihua.model.web.basecontroller.StrResponseController;
import com.lihua.utils.web.WebUtils;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerExecutionChain;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;

/**
 * 用户未认证处理器
 * <p>
 * 若访问接口时未认证，将走该处理器统一返回 JSON 格式的错误信息。
 */
@Component
@Slf4j
public class AuthenticationEntryPointImpl extends StrResponseController implements AuthenticationEntryPoint {

    @Resource
    private RequestMappingHandlerMapping requestMappingHandlerMapping;

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) {
        try {
            // 判断是否为合法请求路径
            HandlerExecutionChain handler = requestMappingHandlerMapping.getHandler(request);
            if (handler == null) {
                // 非法路径，返回 404 错误
                WebUtils.renderJson(response, error(ResultCodeEnum.RESOURCE_NOT_FOUND_ERROR));
                return;
            }
        } catch (Exception e) {
            // 获取 handler 出错也视为 404
            log.warn("获取请求处理器失败: {}", e.getMessage());
            WebUtils.renderJson(response, error(ResultCodeEnum.RESOURCE_NOT_FOUND_ERROR));
            return;
        }

        // 认证失败，记录日志，返回 401
        log.warn("认证失败：{}", authException.getMessage());
        WebUtils.renderJson(response, error(ResultCodeEnum.AUTHENTICATION_EXPIRED));
    }
}

-- 添加 open_userid 字段到 members 表
-- 用于区分企业内部真实userid和第三方应用可见的加密userid

ALTER TABLE members 
ADD COLUMN open_userid VARCHAR(128) DEFAULT NULL AFTER userid,
ADD INDEX idx_open_userid (open_userid);

-- 添加注释
ALTER TABLE members 
MODIFY COLUMN userid VARCHAR(128) NOT NULL COMMENT '企业内部真实userid',
MODIFY COLUMN open_userid VARCHAR(128) DEFAULT NULL COMMENT '服务商主体下的加密userid（第三方应用可见）';


-- 建庫 & 切庫
CREATE DATABASE IF NOT EXISTS petshop
  -- Sets the database’s default character set to utf8mb4 (full Unicode support, including emoji).
  DEFAULT CHARACTER SET utf8mb4
  -- Sets the default collation to utf8mb4_unicode_ci (Unicode-aware, case-insensitive string comparison/sorting).
  COLLATE utf8mb4_unicode_ci;
USE petshop;

-- 品牌
-- UNIQUE KEY set the element inside () become the only one, and make a index name uk_xxx_xxx for faster searching in sql
-- InnoDB storage engine: enables transactions, row-level locking, foreign keys, and crash recovery.
CREATE TABLE IF NOT EXISTS brands (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(191) NOT NULL,
  slug VARCHAR(191) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_brands_name ON brands(name),
  UNIQUE KEY uk_brands_slug (slug)
) ENGINE=InnoDB;

-- 分類（可階層）
-- CONSTRAINT set the condition for foreign key
CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  parent_id INT NULL,
  name VARCHAR(191) NOT NULL,
  slug VARCHAR(191) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_categories_slug (slug),
  KEY idx_categories_parent (parent_id),
  CONSTRAINT fk_categories_parent
    FOREIGN KEY (parent_id) REFERENCES categories (id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 產品
-- TINYINT means only 1 or 0, 1 means active, 0 means deactive
CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  brands_id INT NOT NULL,
  category_id INT NOT NULL,
  name VARCHAR(191) NOT NULL,
  slug VARCHAR(191) NOT NULL,
  description TEXT NULL,
  main_image VARCHAR(512) NULL,
  is_active TINYINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_products_slug (slug),
  KEY idx_products_category (category_id),
  KEY idx_products_brands (brands_id),
  KEY idx_products_name (name),
  CONSTRAINT fk_products_categories
    FOREIGN KEY (category_id) REFERENCES categories (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_products_brands
    FOREIGN KEY (brands_id) REFERENCES brands (id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 產品規格/變體
CREATE TABLE IF NOT EXISTS product_variants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  sku VARCHAR(191) NOT NULL,
  option_text VARCHAR(191) NULL,
  price INT NOT NULL,
  list_price INT NULL,
  weight_g INT NULL,
  stock_qty INT NOT NULL DEFAULT 0,
  is_active TINYINT NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_variant_sku (sku),
  KEY idx_variants_product (products_id),
  CONSTRAINT fk_variants_product
    FOREIGN KEY (products_id) REFERENCES products (id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS members (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name          VARCHAR(100) NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk

PKG_NAME:=network-sentinel
PKG_VERSION:=0.1.0
PKG_RELEASE:=1
PKG_MAINTAINER:=Network Sentinel <sentinel@local>
PKG_LICENSE:=GPL-2.0-only

include $(INCLUDE_DIR)/package.mk

define Package/network-sentinel
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Network Sentinel — plain-English threat briefings
  DEPENDS:=+logread
  PKGARCH:=all
endef

define Package/network-sentinel/description
 Reads firewall and DNS activity from the router and produces short
 plain-English explanations plus a suggested safe action. No automatic
 firewall changes. Phase A: templates; Phase B: optional SLM (SmolLM2-135M
 via llama.cpp or proxy).
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) $(CURDIR)/../src/. $(PKG_BUILD_DIR)/
endef

define Build/Compile
	true
endef

define Package/network-sentinel/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_DIR) $(1)/usr/share/sentinel
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/sentinel-brief $(1)/usr/bin/sentinel-brief
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/collector.sh $(1)/usr/bin/sentinel-collector
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/explainer.sh $(1)/usr/bin/sentinel-explainer
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/slm_brief.sh $(1)/usr/bin/sentinel-slm-brief
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/templates $(1)/usr/share/sentinel/templates
endef

$(eval $(call BuildPackage,network-sentinel))

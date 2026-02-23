# SPDX-License-Identifier: GPL-2.0-only

include $(TOPDIR)/rules.mk

PKG_NAME:=router-assistant
PKG_VERSION:=0.1.0
PKG_RELEASE:=1
PKG_MAINTAINER:=Router Assistant <assist@local>
PKG_LICENSE:=GPL-2.0-only

include $(INCLUDE_DIR)/package.mk

define Package/router-assistant
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Router voice/CLI assistant
  DEPENDS:=+uci
  PKGARCH:=all
endef

define Package/router-assistant/description
 CLI assistant: natural-language-style phrases -> UCI/firewall/network actions.
 Example: "show clients", "block 192.168.1.50", "enable guest wifi".
 No on-device SLM; keyword matching. Optional --dry-run, --yes.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) $(CURDIR)/../src/. $(PKG_BUILD_DIR)/
endef

define Build/Compile
	true
endef

define Package/router-assistant/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_DIR) $(1)/usr/share/router-assistant
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/router-assist $(1)/usr/bin/router-assist
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/parser.sh $(1)/usr/share/router-assistant/parser.sh
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/executor.sh $(1)/usr/share/router-assistant/executor.sh
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/voice-api.cgi $(1)/usr/share/router-assistant/voice-api.cgi
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/voice.html $(1)/usr/share/router-assistant/voice.html
endef

$(eval $(call BuildPackage,router-assistant))

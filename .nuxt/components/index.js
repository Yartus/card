export { default as Footer } from '../../components/Footer.vue'
export { default as Header } from '../../components/Header.vue'
export { default as LottieIconSimple } from '../../components/LottieIcon.simple.vue'
export { default as LottieIcon } from '../../components/LottieIcon.vue'
export { default as WecardOptimized } from '../../components/WecardOptimized.vue'
export { default as AdminAssetEditModal } from '../../components/admin/AssetEditModal.vue'
export { default as AdminAssetPreviewModal } from '../../components/admin/AssetPreviewModal.vue'
export { default as AdminAssetUploadModal } from '../../components/admin/AssetUploadModal.vue'
export { default as AssetsAssetCard } from '../../components/assets/AssetCard.vue'
export { default as AssetsAssetFilters } from '../../components/assets/AssetFilters.vue'
export { default as AssetsAssetGrid } from '../../components/assets/AssetGrid.vue'
export { default as AssetsAssetLibraryHeader } from '../../components/assets/AssetLibraryHeader.vue'
export { default as AssetsAssetModal } from '../../components/assets/AssetModal.vue'
export { default as AssetsContactModal } from '../../components/assets/ContactModal.vue'
export { default as CardAnalyticsTracker } from '../../components/card/AnalyticsTracker.vue'
export { default as CardAssetPreview } from '../../components/card/AssetPreview.vue'
export { default as CardBusinessShowcase } from '../../components/card/BusinessShowcase.vue'
export { default as CardHeader } from '../../components/card/CardHeader.vue'
export { default as CardPreview } from '../../components/card/CardPreview.vue'
export { default as CardCompanyIntro } from '../../components/card/CompanyIntro.vue'
export { default as CardContactInfo } from '../../components/card/ContactInfo.vue'
export { default as CardEnvironmentShowcase } from '../../components/card/EnvironmentShowcase.vue'
export { default as CardLogoWall } from '../../components/card/LogoWall.vue'
export { default as CardProductGallery } from '../../components/card/ProductGallery.vue'
export { default as CardQuickActions } from '../../components/card/QuickActions.vue'
export { default as CardSharePanel } from '../../components/card/SharePanel.vue'
export { default as CardShopDirect } from '../../components/card/ShopDirect.vue'
export { default as CardShopDirectBlock } from '../../components/card/ShopDirectBlock.vue'
export { default as CardSloganSection } from '../../components/card/SloganSection.vue'
export { default as CardSocialLinks } from '../../components/card/SocialLinks.vue'
export { default as CardSolutionIntro } from '../../components/card/SolutionIntro.vue'
export { default as CardStandardGrid } from '../../components/card/StandardGrid.vue'
export { default as CardTimeline } from '../../components/card/Timeline.vue'
export { default as CardTrustCredentials } from '../../components/card/TrustCredentials.vue'
export { default as CardVcardGenerator } from '../../components/card/VcardGenerator.vue'
export { default as CardVideoShowcase } from '../../components/card/VideoShowcase.vue'
export { default as WorkspaceAssetEditorModal } from '../../components/workspace/AssetEditorModal.vue'
export { default as WorkspaceAssetsContentEditor } from '../../components/workspace/AssetsContentEditor.vue'
export { default as WorkspaceAssetsCoverEditor } from '../../components/workspace/AssetsCoverEditor.vue'
export { default as WorkspaceAssetsLibrary } from '../../components/workspace/AssetsLibrary.vue'
export { default as WorkspaceAssetsPreviewPanel } from '../../components/workspace/AssetsPreviewPanel.vue'
export { default as WorkspaceConfigArea } from '../../components/workspace/ConfigArea.vue'
export { default as WorkspaceModuleLibrary } from '../../components/workspace/ModuleLibrary.vue'
export { default as WorkspacePreviewPanel } from '../../components/workspace/PreviewPanel.vue'
export { default as WorkspaceConfigAvatarEditor } from '../../components/workspace/config/AvatarEditor.vue'
export { default as WorkspaceConfigBackgroundEditor } from '../../components/workspace/config/BackgroundEditor.vue'
export { default as WorkspaceConfigCardPreviewDisplay } from '../../components/workspace/config/CardPreviewDisplay.vue'
export { default as WorkspaceConfigCardPreviewEditor } from '../../components/workspace/config/CardPreviewEditor.vue'
export { default as WorkspaceConfigCompanyIntroConfig } from '../../components/workspace/config/CompanyIntroConfig.vue'
export { default as WorkspaceConfigContactVisibilityConfig } from '../../components/workspace/config/ContactVisibilityConfig.vue'
export { default as WorkspaceConfigHeaderBackgroundConfig } from '../../components/workspace/config/HeaderBackgroundConfig.vue'
export { default as WorkspaceConfigHeaderConfig } from '../../components/workspace/config/HeaderConfig.vue'
export { default as WorkspaceConfigLogoConfig } from '../../components/workspace/config/LogoConfig.vue'
export { default as WorkspaceConfigLogoWallConfig } from '../../components/workspace/config/LogoWallConfig.vue'
export { default as WorkspaceConfigPushConfigSection } from '../../components/workspace/config/PushConfigSection.vue'
export { default as WorkspaceConfigShopDirectConfig } from '../../components/workspace/config/ShopDirectConfig.vue'
export { default as WorkspaceConfigStandardGridConfig } from '../../components/workspace/config/StandardGridConfig.vue'
export { default as WorkspaceConfigTimelineConfig } from '../../components/workspace/config/TimelineConfig.vue'
export { default as WorkspaceConfigTrustCredentialsConfig } from '../../components/workspace/config/TrustCredentialsConfig.vue'
export { default as WorkspaceConfigVideoShowcaseConfig } from '../../components/workspace/config/VideoShowcaseConfig.vue'
export { default as WorkspaceConfigUploadLimits } from '../../components/workspace/config/upload-limits.js'
export { default as WorkspaceFormBlockEditor } from '../../components/workspace/form/BlockEditor.vue'
export { default as WorkspaceFormColorPicker } from '../../components/workspace/form/ColorPicker.vue'
export { default as WorkspaceFormIconPicker } from '../../components/workspace/form/IconPicker.vue'
export { default as WorkspaceFormIconSelector } from '../../components/workspace/form/IconSelector.vue'
export { default as WorkspaceFormImageUpload } from '../../components/workspace/form/ImageUpload.vue'
export { default as WorkspaceFormMediaSelector } from '../../components/workspace/form/MediaSelector.vue'
export { default as WorkspaceFormShopDirectBlockEditor } from '../../components/workspace/form/ShopDirectBlockEditor.vue'
export { default as WorkspaceFormTextInput } from '../../components/workspace/form/TextInput.vue'

// nuxt/nuxt.js#8607
function wrapFunctional(options) {
  if (!options || !options.functional) {
    return options
  }

  const propKeys = Array.isArray(options.props) ? options.props : Object.keys(options.props || {})

  return {
    render(h) {
      const attrs = {}
      const props = {}

      for (const key in this.$attrs) {
        if (propKeys.includes(key)) {
          props[key] = this.$attrs[key]
        } else {
          attrs[key] = this.$attrs[key]
        }
      }

      return h(options, {
        on: this.$listeners,
        attrs,
        props,
        scopedSlots: this.$scopedSlots,
      }, this.$slots.default)
    }
  }
}

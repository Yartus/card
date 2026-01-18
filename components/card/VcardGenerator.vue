<template>
  <pre v-show="false" ref="vCard">
BEGIN:VCARD
VERSION:3.0
N;CHARSET=UTF-8:{{ getSplitName }}
FN:{{ getFullname }}
ORG:{{ cardData.ORG }}
COMPANY:{{ cardData.COMPANY }}
TITLE:{{ cardData.TITLE }}
ADR;CHARSET=UTF-8;TYPE=WORK:;;{{ cardData.ADDRESS }}
TEL;TYPE=Work,pref:{{ cardData.TEL1 }}
TEL;CELL;TYPE=Mobile,VOICE:{{ cardData.MOB }}
TEL;TYPE=WORK,VOICE:{{ cardData.WORK }}
TEL;TYPE=Work,Fax:{{ cardData.FAX }}
TEL;TYPE=Home,VOICE:{{ cardData.HOME }}
EMAIL;TYPE=Email:{{ cardData.EMAIL }}
URL;TYPE=Website:{{ cardData.website }}
URL;TYPE=WeChat:{{ cardData.WeChat }}
{{ getURLs }}
PHOTO;ENCODING=b:{{ cardData.PHOTO }}
NOTE;CHARSET=UTF-8:{{ cardData.NOTE }}
UID:{{ cardData.UID }}
END:VCARD</pre>
</template>

<script>
export default {
  name: 'VcardGenerator',
  
  props: {
    cardData: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  
  computed: {
    getURLs() {
      if (!this.cardData.urls || !Array.isArray(this.cardData.urls)) {
        return ''
      }
      return this.cardData.urls.map(e => `URL;TYPE=${e.title}:${e.url}`).join('\n')
    },
    
    getSplitName() {
      const fn = this.cardData.fn || ''
      const ln = this.cardData.ln || ''
      return `${ln};${fn};;;`
    },
    
    getFullname() {
      const fn = this.cardData.fn || ''
      const ln = this.cardData.ln || ''
      return `${fn} ${ln}`.trim()
    }
  },
  
  methods: {
    // 生成vCard数据
    generateVcard() {
      return this.$refs.vCard ? this.$refs.vCard.innerText : ''
    },
    
    // 下载vCard文件
    downloadVcard(filename = 'contact.vcf') {
      const vcardData = this.generateVcard()
      const blob = new Blob([vcardData], { type: 'text/vcard;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
/* 隐藏的组件，无需样式 */
</style>

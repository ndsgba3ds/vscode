Page({

  /**
   * 页面的初始数据
   */
  data: {
    url: 'http://127.0.0.1:8000/media',
    content:'',
    score:5,
    starDesc: '非常满意，无可挑剔',
    stars: [{
      lightImg: '/images/star_light.png',
      blackImg: '/images/star_black.png',
      flag: 1,
      message: '非常不满意，各方面都很差'
    }, {
      lightImg: '/images/star_light.png',
      blackImg: '/images/star_black.png',
      flag: 1,
      message: '不满意，比较差'
    }, {
      lightImg: '/images/star_light.png',
      blackImg: '/images/star_black.png',
      flag: 1,
      message: '一般，还要改善'
    }, {
      lightImg: '/images/star_light.png',
      blackImg: '/images/star_black.png',
      flag: 1,
      message: '比较满意，仍要改善'
    }, {
      lightImg: '/images/star_light.png',
      blackImg: '/images/star_black.png',
      flag: 1,
      message: '非常满意，无可挑剔'
    }],
    assessLists: ['意见很有帮助', '态度非常好', '非常敬业', '非常专业认真', '回复很及时', '耐心细致'],
    assessSelect: -1,
    employee:[]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var t = this
    wx.request({
      url: 'http://127.0.0.1:8000/api/get_employee_by_id',
      method: 'GET',
      header: {
        "Content-Type": "application/json"
      },
      data: {
        employee_id:options.employee_id
      },
      success: function (res) {
        if (res.data.code == 200) {
          t.setData({
            employee: res.data.data
          })

        } else {
          wx.showModal({
            title: '提示',
            showCancel: false,
            content: '获取失败',
          })
        }
      }
    });
  },
  // 选择评价星星
  starClick: function (e) {
    var that = this;
    for (var i = 0; i < that.data.stars.length; i++) {
      var allItem = 'stars[' + i + '].flag';
      that.setData({
        [allItem]: 2
      })
    }
    var index = e.currentTarget.dataset.index;
    for (var i = 0; i <= index; i++) {
      var item = 'stars[' + i + '].flag';
      that.setData({
        [item]: 1
      })
    }
    this.setData({
      starDesc: this.data.stars[index].message
    })
    this.setData({
      score:index+1
    })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },

  /**
   * 输入框
   */
  contentInput:function(e){
    var val = e.detail.value;
    this.setData({
      content: val
    })
  },

  /**
   * 标签选择
   */
  assessSelection:function(e){
    this.setData({//把选中值放入判断值
      assessSelect: e.currentTarget.dataset.select
    })
  },

  /**
   * 提交
   */
  submit:function(e){
    var that = this;
    wx.login({
      success: function (res) {
        var userInfo = e.detail.userInfo;
        var code=res.code;
        wx.request({
          url: 'http://127.0.0.1:8000/api/wx_login',
          method: 'POST',
          header:{
            "Content-Type": "application/json"
          },
          data: {
            code:code,
            nickName:userInfo.nickName,
            avatarUrl:userInfo.avatarUrl
            },
          success: function (res) {
            
            if (res.data.code == 200) {  
              if(that.data.content){
                wx.request({
                  url: 'http://127.0.0.1:8000/api/add_comment',
                  method: 'POST',
                  header: {
                    "Content-Type": "application/json"
                  },
                  data: {
                    openId: res.data.data.userInfo.openId,
                    employeeId: that.data.employee.id,
                    content: that.data.content,
                    score:that.data.score
                  },
                  success: function (res) {
                    console.log(res.data)
                    if (res.data.code == 200) {  
                      wx.showToast({
                        title: '提交成功',
                        icon: 'succes',
                        duration: 3000,
                        mask: true,
                        success:function(){
                          wx.navigateTo({
                            url: '../scratch/scratch?open_id=' + res.data.data.userInfo.openId,
                          })
                        }
                      })
                    }else if(res.data.code==201){
                      wx.showToast({
                        title: '今天已评论！',
                        icon: 'succes',
                        duration: 3000,
                        mask: true,
                        success:function(){
                          wx.navigateTo({
                            url: '../scratch/scratch'                        })
                        }
                      })
                    }
                  }
                });
              }else{
                wx.showModal({
                  title: '提示',
                  showCancel: false,
                  content: '不能为空',
                })
              }
            } else {
              wx.showModal({
                title: '提示',
                showCancel: false,
                content: '获取openid失败',
              })
            }
          }
        });
      }
    });
  }
})
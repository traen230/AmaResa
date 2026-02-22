async function handleAppToExt(e) {
  browser.storage.sync.set({
    appToExtData: {
      cameFromApp: true,
      tool: e.detail.tool,
    },
  });

  window.open('https://studio.youtube.com', '_blank');
}
window.addEventListener('appToExt', handleAppToExt, false);

/**
 *
 * interface postMessage {
 *     type: string, // always set to lifeCycleResponse
 *     error: boolean,
 *     data: string // for now, not sure if we need anything else
 * }
 *
 * Ideally we should be using extension message api but this will do for now
 */
async function handleLifeCycleDeepLink(e) {
  const url = document.location.href.includes('localhost') ? 'http://localhost:7265' : 'https://www.tubebuddy.com';
  const { detail } = e;

  const validFeatures = {
    // youtube
    yt: {
      nicheinsights: 'Niche Insights',
    },
    // youtube studio
    yts: {
      suggestedshorts: 'Suggested Shorts',
      keywordexplorer: 'Keyword Explorer',
      seostudio: 'SEO Studio',
      thumbnailanalyzer: 'Thumbnail Analyzer',
      titlegenerator: 'Title Generator',
      relatedvideomanager: 'Related Video Manager',
    },
  };

  const allowedFeatures = [...Object.values(validFeatures.yt), ...Object.values(validFeatures.yts)];

  // If not coming from a site we know we don't do anything as a security measure
  if (!e.srcElement.origin.includes('localhost') && !e.srcElement.origin.includes('tubebuddy')) {
    window.postMessage({ type: 'lifeCycleResponse', success: false, data: 'not from known site' }, url);
    return;
  }

  // Need to improve this logic a little bit so we are validating event source e should contain where the message is coming from
  if (!allowedFeatures.includes(detail.tool)) {
    window.postMessage({ type: 'lifeCycleResponse', success: false, data: 'unknown event' }, url);
    return;
  }

  await browser.storage.sync.set({
    LifeCycleDeepLinkData: { ...e.detail },
  });

  window.postMessage({ type: 'lifeCycleResponse', success: true, data: '' }, url);

  // Opening new tab
  if (detail.redirectURL.includes('studio')) {
    if (detail.properties.videoid) {
      window.open(`https://studio.youtube.com/video/${detail.properties.videoid}/edit`, '_blank');
    } else if (detail.properties.contenttab && detail.properties.channelid) {
      window.open(`https://studio.youtube.com/channel/${detail.properties.channelid}/videos/${detail.properties.contenttab}`, '_blank');
    } else {
    // We probably shouldn't do this right now until we need to launch videos that don't need a videoId
      window.open('https://studio.youtube.com/', '_blank');
    }
  }

  if (!detail.redirectURL.includes('studio')) {
    await browser.storage.sync.set({ userPrefShowToolbox: true });
    window.open(detail.redirectURL);
  }
}

window.addEventListener('lifeCycleDeepLink', handleLifeCycleDeepLink, false);

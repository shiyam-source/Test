#!/bin/bash
# Run Lighthouse sequentially: each page x {staging, prod} x {mobile, desktop} x N runs.
# Third-party tags are blocked on BOTH sites so the comparison isolates the platform (Webflow vs Sanity build).
S=/tmp/claude-0/-home-user-Test/fb647a80-1772-5a33-98bf-885a44633475/scratchpad
LH=$S/lh/node_modules/.bin/lighthouse
OUT=$S/lhr; mkdir -p $OUT
CHROME=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome | head -1)
BLOCK='--blocked-url-patterns=*googletagmanager.com* --blocked-url-patterns=*google-analytics.com* --blocked-url-patterns=*doubleclick.net* --blocked-url-patterns=*analytics.google.com* --blocked-url-patterns=*www.google.com/* --blocked-url-patterns=*cookiebot.com* --blocked-url-patterns=*hs-scripts.com* --blocked-url-patterns=*hs-analytics.net* --blocked-url-patterns=*hsforms* --blocked-url-patterns=*licdn.com* --blocked-url-patterns=*clarity.ms* --blocked-url-patterns=*facebook.net* --blocked-url-patterns=*lfeeder.com* --blocked-url-patterns=*happierleads.com* --blocked-url-patterns=*popt.in* --blocked-url-patterns=*albacross.com* --blocked-url-patterns=*dyh8ken8pc.com* --blocked-url-patterns=*apollo.io* --blocked-url-patterns=*snitcher.com* --blocked-url-patterns=*visitortracking.com* --blocked-url-patterns=*getwarmly.com* --blocked-url-patterns=*svrdntfctn.com* --blocked-url-patterns=*vector.co* --blocked-url-patterns=*ddwl4m2hdecbv.cloudfront.net* --blocked-url-patterns=*cloudflareinsights.com*'
RUNS_M=${RUNS_M:-3}; RUNS_D=${RUNS_D:-2}
for page in "$@"; do
  slug=$(echo "$page" | sed 's#^/##; s#/#_#g'); [ -z "$slug" ] && slug=home
  for site in stg prd; do
    [ $site = stg ] && host=https://staging.tripledart.com || host=https://www.tripledart.com
    for form in mobile desktop; do
      [ $form = mobile ] && n=$RUNS_M && preset="" || { n=$RUNS_D; preset="--preset=desktop"; }
      for i in $(seq 1 $n); do
        f=$OUT/${slug}__${site}__${form}__$i.json
        [ -s "$f" ] && continue
        timeout 180 $LH "$host$page" $preset $BLOCK --output=json --output-path="$f" --quiet \
          --only-categories=performance,accessibility,best-practices,seo \
          --chrome-path="$CHROME" --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage" >/dev/null 2>>$OUT/errors.log \
          || echo "FAIL $slug $site $form $i" >> $OUT/errors.log
        echo "$(date +%T) $slug $site $form $i"
      done
    done
  done
done

#!/bin/bash
# scripts/test_e2e_demo.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
BLUE='\033[1;34m'

PASSED=0

echo -e "${BLUE}--- AuraQA E2E Demo ---${NC}"

# Check 1
echo "1. Checking backend health..."
HEALTH_RES=$(curl -s http://localhost/api/health)
if echo "$HEALTH_RES" | grep -q '"status":"healthy"'; then
  echo -e "${GREEN}PASS: Health endpoint returned healthy${NC}"
  ((PASSED++))
else
  echo -e "${RED}FAIL: Health endpoint did not return healthy: $HEALTH_RES${NC}"
fi

PAYLOAD='{
  "test_case_id": "TC-123",
  "test_suite_id": "TS-001",
  "broken_selector": "#submit-btn",
  "selector_type": "css",
  "dom_snapshot": "<html><body><button id=\"new-submit-btn\" class=\"btn primary\">Submit</button></body></html>",
  "original_element_attributes": {
    "tag": "button",
    "element_id": "submit-btn",
    "classes": ["btn", "primary"],
    "text": "Submit",
    "attributes": {},
    "data_testid": null,
    "depth": 2,
    "parent_tag": "body"
  },
  "page_url": "http://localhost:5173/login",
  "screenshot_base64": null,
  "error_message": "Selector not found",
  "timestamp": "2024-05-27T00:00:00Z",
  "environment": "staging",
  "retry_count": 0
}'

echo "2. Sending POST /api/heal..."
RESPONSE=$(curl -s -X POST http://localhost/api/heal \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

STATUS=$(echo "$RESPONSE" | jq -r '.status')
CONFIDENCE=$(echo "$RESPONSE" | jq -r '.confidence')
SELECTOR=$(echo "$RESPONSE" | jq -r '.healed_selector')

echo "Check 2: Validating heal status..."
if [[ "$STATUS" == "healed" || "$STATUS" == "escalated" ]]; then
    echo -e "${GREEN}PASS: Status is valid ('$STATUS')${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL: Invalid status: $STATUS (Raw response: $RESPONSE)${NC}"
fi

echo "Check 3: Validating confidence score..."
if [[ "$CONFIDENCE" != "null" ]] && awk "BEGIN {exit !($CONFIDENCE >= 0 && $CONFIDENCE <= 100)}"; then
    echo -e "${GREEN}PASS: Confidence is valid ($CONFIDENCE)${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL: Invalid confidence: $CONFIDENCE${NC}"
fi

echo "Check 4: Validating healed_selector..."
if [[ "$SELECTOR" != "null" && -n "$SELECTOR" ]]; then
    echo -e "${GREEN}PASS: Healed selector found ('$SELECTOR')${NC}"
    ((PASSED++))
else
    echo -e "${RED}FAIL: Healed selector is empty${NC}"
fi

echo -e "\n${BLUE}AuraQA E2E Demo: ${PASSED}/4 checks passed${NC}"

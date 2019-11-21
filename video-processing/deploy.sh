set -e

STACK_NAME=video-processing-demo-$(date +%s)

# init nas and vpc
fun nas init

# sync .fun/nas/auto-default/wb-video-demo/ffmpeg to nas, then you can use /mnt/auto/ffmpeg when excute funtion
# you can download latest ffmpeg at https://www.johnvansickle.com/ffmpeg/
fun nas sync

# Deploy FC functions
fun deploy

# Authorize FnF to assume role to invoke FC functions
aliyun ram UpdateRole --RoleName aliyunfcgeneratedrole-$REGION-wb-video-demo --NewAssumeRolePolicyDocument "$(cat ./assume-role-policy.json)"


if [ "$ACTION" == "create" ]; then
  # Create FnF flows and the MNS queue
  aliyun ros CreateStack --RegionId $REGION --StackName $STACK_NAME --TimeoutInMinutes 10 \
    --TemplateBody "$(cat ./ros-template.json)" \
    --Parameters.1.ParameterKey DefinitionFC \
    --Parameters.1.ParameterValue "$(cat ./flows/video-processing-fc.yaml)" \
    --Parameters.2.ParameterKey RoleArn \
    --Parameters.2.ParameterValue acs:ram::$ACCOUNT_ID:role/aliyunfcgeneratedrole-$REGION-wb-video-demo \
    --Parameters.3.ParameterKey FlowNameFC \
    --Parameters.3.ParameterValue $FLOW_NAME-"fc"
elif [ "$ACTION" == "update" ]; then
  # Create FnF flows and the MNS queue
  aliyun ros UpdateStack --RegionId $REGION --StackId $STACK_ID --TimeoutInMinutes 10 \
    --TemplateBody "$(cat ./ros-template.json)" \
    --Parameters.1.ParameterKey DefinitionFC \
    --Parameters.1.ParameterValue "$(cat ./flows/video-processing-fc.yaml)" \
    --Parameters.2.ParameterKey RoleArn \
    --Parameters.2.ParameterValue acs:ram::$ACCOUNT_ID:role/aliyunfcgeneratedrole-$REGION-wb-video-demo \
    --Parameters.3.ParameterKey FlowNameFC \
    --Parameters.3.ParameterValue $FLOW_NAME-"fc"
fi


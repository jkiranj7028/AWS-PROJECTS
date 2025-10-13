#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MyCdkAppStack } from '../lib/my-cdk-app-stack';

const app = new cdk.App();
new MyCdkAppStack(app, 'MyCdkAppStack');

# Copyright 2020 Tensorforce Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from tensorforce import TensorforceError
from tensorforce.core import tf_function
from tensorforce.core.optimizers import UpdateModifier


class UpdateModifierWrapper(UpdateModifier):
    """
    Update modifier wrapper (specification key: `update_modifier_wrapper`).

    Args:
        optimizer (specification): Optimizer configuration
            (<span style="color:#C00000"><b>required</b></span>).
        clipping_threshold (parameter, float > 0.0): Clipping threshold
            (<span style="color:#00C000"><b>default</b></span>: no clipping).
        multi_step (parameter, int >= 1): Number of optimization steps
            (<span style="color:#00C000"><b>default</b></span>: single step).
        subsampling_fraction (parameter, 0.0 < float <= 1.0): Fraction of batch timesteps to
            subsample (<span style="color:#00C000"><b>default</b></span>: no subsampling).
        linesearch_iterations (parameter, int >= 0):  Maximum number of line search iterations
            (<span style="color:#00C000"><b>default</b></span>: no line search).
        name (string): (<span style="color:#0000C0"><b>internal use</b></span>).
        arguments_spec (specification): <span style="color:#0000C0"><b>internal use</b></span>.
    """

    def __init__(
        self, optimizer, *, multi_step=1, subsampling_fraction=1.0, clipping_threshold=None,
        linesearch_iterations=0, name=None, arguments_spec=None,
        # Deprecated
        optimizing_iterations=None, **kwargs
    ):
        if optimizing_iterations is not None:
            raise TensorforceError.deprecated(
                name='Optimizer', argument='optimizing_iterations',
                replacement='linesearch_iterations'
            )

        optimizer = dict(type=optimizer)
        optimizer.update(kwargs)

        if linesearch_iterations > 0:
            optimizer = dict(
                type='linesearch_step', optimizer=optimizer, max_iterations=linesearch_iterations
            )

        if subsampling_fraction != 1.0:
            optimizer = dict(
                type='subsampling_step', optimizer=optimizer, fraction=subsampling_fraction
            )

        if multi_step > 1:
            optimizer = dict(type='multi_step', optimizer=optimizer, num_steps=multi_step)

        if clipping_threshold is not None:
            optimizer = dict(
                type='clipping_step', optimizer=optimizer, threshold=clipping_threshold
            )

        super().__init__(optimizer=optimizer, name=name, arguments_spec=arguments_spec)

    @tf_function(num_args=1)
    def step(self, *, arguments, variables, **kwargs):
        return self.optimizer.step(arguments=arguments, variables=variables, **kwargs)

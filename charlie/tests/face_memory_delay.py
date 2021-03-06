# -*- coding: utf-8 -*-
"""
face_memory_delay: The Penn face memory test, delayed.

This is the second part of the Penn face memory test [1]. Each trial comprises
a face (either an old face or a new one), and probands make old/new judgements.
It is identical to the original Penn test.

Summary statistics:

    ntrials : number of trials.
    ncorrect : number of correct trials.
    pcorrect : proportion of trials correct.
    dprime : index of sensitivity.
    criterion : index of bias.
    rt_mean : mean response time on correct trials in milliseconds.
    rt_mean_outrmvd : as above, except any trials <> 3 s.d. of mean excluded.
    rt_outrmvd : number of outlier trials.

References:

[1] Gur, R.C., Ragland, J.D., Mozley, L.H., Mozley, P.D., Smith, R., Alavi, A.,
et al. (1997). Lateralized changes in regional cerebral blood flow during
performance of verbal and facial recognition tasks: Correlations with
performance and ”effort”. Brain Cogn., 33:388-414.

"""
__version__ = 1.0
__author__ = 'Sam Mathias'

import pandas
import charlie.tools.visual as visual
import charlie.tools.data as data
import charlie.tools.events as events
import charlie.tools.summaries as summaries
import charlie.tools.batch as batch

output_format = [
    ('proband_id', str),
    ('test_name', str),
    ('phase', str),
    ('trialn', int),
    ('f', str),
    ('ans', str),
    ('rsp', str),
    ('rt', int)
]
test_name = 'face_memory_delay'
stim_order = [34, 12, 28, 37, 22, 17, 2, 13, 32, 23, 8, 20, 14, 38, 7, 31, 26,
              3, 5, 15, 10, 24, 36, 1, 9, 39, 18, 19, 33, 0, 35, 30, 6, 4, 27,
              11, 21, 16, 29, 25]
black_bg = True

def control_method(proband_id, instructions):
    """
    Generates a control iterable. For this test, it is a list of tuples in
    the format (proband_id, test_name, phase, trialn, f, ans).
    """
    p = data.pj(data.VISUAL_PATH, test_name)
    stimuli = sorted(f for f in data.ld(p) if 'bmp' in f)
    labels = instructions[-2:]

    targets = sorted(data.pj(p, f) for f in stimuli if 'tar' in f)
    distractors = sorted([data.pj(p, f) for f in stimuli if 'ddis' in f])
    stimuli = [j for i, j in sorted(zip(stim_order, targets + distractors))]
    control = [(proband_id, test_name, 'test', i, f,
                labels['tar' not in f]) for i, f in enumerate(stimuli)]

    return control


def trial_method(screen, instructions, trial_info):
    """
    Runs a single trial of the test.
    """

    proband_id, _, _, trialn, f, ans = trial_info
    img_pos = (0,-100)
    labels = instructions[-2:]
    if not screen.wordzones:
        screen.load_keyboard_keys()
        screen.create_keyboard_key_zones(('l', 'r'), 200, 250)
        screen.create_word_zones(labels, 200, 350)

    # show instructions if first trial
    if not trialn:
        rsp = screen.splash(instructions[0], mouse=False)
        if rsp == 'EXIT':
            return 'EXIT'
        screen.wipe()
        screen.countdown_splash(5, instructions[1])
        screen.wipe()

    # set up trial
    img = screen.images[f]
    p = labels, [visual.DEFAULT_TEXT_COLOUR] * len(labels)
    screen.change_word_colour(*p)
    screen.change_key_colour(('l','r'), ('',''))
    screen.blit_image(img, img_pos, update=False)
    screen.update()

    # wait for a response
    keys = [276, 275]
    keydown = events.wait_for_valid_keydown(keys, 'key')   
    if keydown == 'EXIT':
        return 'EXIT'
    else:
        k, rt = keydown
    rsp = dict(zip(keys,labels))[k]
    rspk = dict(zip(keys,('l', 'r')))[k]

    # update screen
    screen.change_word_colour(rsp, visual.BLUE)
    screen.change_key_colour(rspk, 'b', update=False)
    screen.update()
    events.wait(events.DEFAULT_ITI_NOFEEDBACK)
    screen.wipe(img.get_rect(center=img_pos))

    # return trial outcome
    trial_info = tuple(list(trial_info) + [rsp, rt])

    return trial_info


def summary_method(data_obj, instructions):
    """
    Computes summary stats for this task.
    """
    df = data_obj.to_df()
    df = df[df.phase == 'test']
    labels = instructions[-2:]
    signal, noise = labels

    stats = summaries.get_universal_stats(data_obj)
    stats += summaries.get_accuracy_stats(df, '')
    stats += summaries.get_rt_stats(df, '')
    stats += summaries.get_sdt_stats(df, noise, signal, '')
    df = summaries.make_df(stats)

    return df


if __name__ == '__main__':
    batch.run_single_test(test_name)